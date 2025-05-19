import glob
import json
import logging
import os
from pathlib import Path
from datetime import datetime

from langchain_community.document_loaders import JSONLoader, DirectoryLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import VertexAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_transformers import EmbeddingsRedundantFilter
import shutil

from statschat import load_config
from statschat.embedding.latest_updates import (
    find_latest,
    compare_latest,
    unflag_former_latest,
    update_split_documents,
    find_matching_chunks,
)


class UpdateVectorStore(DirectoryLoader, JSONLoader):
    """
    Leveraging Langchain classes to split pre-scraped publication
    JSONs to section-level JSONs and loading to document
    store
    """

    def __init__(
        self,
        latest_directory: Path = "data/latest_json_conversions",
        latest_split_directory: Path = "data/latest_json_split",
        split_length: int = 1000,
        split_overlap: int = 100,
        embedding_model_name: str = "sentence-transformers/all-mpnet-base-v2",
        redundant_similarity_threshold: float = 0.99,
        faiss_db_root: str = "data/db_langchain",
        logger: logging.Logger = None,
        latest_only: bool = False,
    ):
        self.latest_directory = latest_directory
        self.latest_split_directory = latest_split_directory
        self.split_length = split_length
        self.split_overlap = split_overlap
        self.embedding_model_name = embedding_model_name
        self.redundant_similarity_threshold = redundant_similarity_threshold
        self.faiss_db_root = faiss_db_root + ("_latest" if latest_only else "")
        self.latest_only = latest_only
        self.temp_faiss_db_root = "temp_faiss_db"

        # Initialise logger
        if logger is None:
            self.logger = logging.getLogger(__name__)

        else:
            self.logger = logger

        # Only if temp latest_directory exists i.e. new inbound
        # publications have been webscraped and stored
        if os.path.exists(self.latest_directory):
            if self.latest_only:
                self.logger.info("Treating 'latest' flags")
                self._treat_latest()
            self.logger.info("Split full publication JSONs into sections")
            self._json_splitter()
            self.logger.info("Load section JSONs to memory")
            self._load_json_to_memory()
            self.logger.info("Instantiate embeddings")
            self._instantiate_embeddings()
            self.logger.info("Filtering out duplicate docs")
            self._drop_redundant_documents()
            self.logger.info("Chunk documents")
            self._split_documents()
            self.logger.info("Vectorise docs and commit to physical vector store")
            self._embed_documents()
            self.logger.info("Merging into existing FAISS DB")
            self._merge_faiss_db()

        else:
            self.logger.info("Aborting: no new documents to be added")

        return None

    def _treat_latest(self):
        """
        Checks for inbound publications which are latest versions in a series.
        Revokes 'latest' flag to False for outdated versions.
        Locates all chunks related to these outdated versions and removes
        them from the vector store.
        """
        self.logger.info("Checking for updates to 'latest'")
        latest_filepaths = find_latest(self.latest_directory)
        _, former_latest = compare_latest(self.latest_directory, latest_filepaths)
        self.logger.info(f"Number of outdated latest flags: {len(former_latest)}")

        embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model_name)
        db = FAISS.load_local(
            self.faiss_db_root, embeddings, allow_dangerous_deserialization=True
        )
        db_dict = db.docstore._dict
        self.logger.info(
            f"Number of chunks in vector store PRE-edit: {len(db.docstore._dict)}"
        )

        if len(former_latest) > 0:
            self.logger.info("Revoking expired latest flags")
            unflag_former_latest(self.latest_directory, former_latest)
            update_split_documents(self.latest_split_directory, former_latest)
            self.logger.info("Removing expired latest chunks from vector store")
            chunks = find_matching_chunks(db_dict, former_latest)
            self.logger.info(
                f"Number of chunks to be removed from vector store: {len(chunks)}"
            )
            if len(chunks) > 0:
                db.delete(chunks)
            db.save_local(self.faiss_db_root)
        else:
            self.logger.info("No outdated 'latest' flags requiring updates")

        return None

    def _json_splitter(self):
        """
        Splits scraped json to multiple json,
        one for each publication section
        """

        # create storage folder for split publications
        isExist = os.path.exists(self.latest_split_directory)
        if not isExist:
            os.makedirs(self.latest_split_directory)

        found_publications = glob.glob(f"{self.latest_directory}/*.json")
        self.logger.info(f"Found {len(found_publications)} publications for splitting")

        # extract metadata from each publication section
        # and store as separate JSON
        for filename in found_publications:
            try:
                with open(filename) as file:
                    json_file = json.load(file)
                    if (not (self.latest_only)) or json_file["latest"]:
                        id = json_file["id"][:60]

                        publication_meta = {
                            i: json_file[i] for i in json_file if i != "content"
                        }
                        for num, section in enumerate(json_file["content"]):
                            section_json = {**section, **publication_meta}

                            # Check that there's text extracted for this section
                            if len(section["page_text"]) > 5:
                                with open(
                                    f"{self.latest_split_directory}/{id}_{num}.json",
                                    "w",
                                ) as new_file:
                                    json.dump(section_json, new_file, indent=4)

            except KeyError as e:
                self.logger.warning(f"Could not parse {filename}: {e}")

        return None

    def _load_json_to_memory(self):
        """
        Loads publication section JSONs to memory
        """

        def metadata_func(record: dict, metadata: dict) -> dict:
            """
            Helper, instructs on how to fetch metadata.  Here I take
            everything that isn't the actual text body.
            """
            # Copy everything
            metadata.update(record)

            # Reformat the date
            metadata["date"] = datetime.strptime(
                metadata.pop("release_date"), "%Y-%m-%d"
            ).__format__("%d %B %Y")

            # Rename a few things
            metadata["source"] = metadata.pop("id")

            # Remove the text from metadata
            metadata.pop("page_text")

            return metadata

        # required argument from JSONLoader class
        # text element required
        json_loader_kwargs = {
            "jq_schema": ".",
            "content_key": "page_text",
            "metadata_func": metadata_func,
        }
        self.logger.info(f"Loading data from {self.latest_split_directory}")
        self.loader = DirectoryLoader(
            self.latest_split_directory,
            glob="*.json",
            use_multithreading=True,
            show_progress=True,
            loader_cls=JSONLoader,
            loader_kwargs=json_loader_kwargs,
        )

        self.docs = self.loader.load()
        self.logger.info(f"{len(self.docs)} publication sections loaded to memory")
        return None

    def _instantiate_embeddings(self):
        """
        Loads embedding model to memory
        """
        if self.embedding_model_name == "textembedding-gecko@001":
            self.embeddings = VertexAIEmbeddings()

        else:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name
            )

        return None

    def _drop_redundant_documents(self):
        """
        Drops document chunks (except one!) above cosine
        similarity threshold
        """
        redundant_filter = EmbeddingsRedundantFilter(
            embeddings=self.embeddings,
            similarity_threshold=self.redundant_similarity_threshold,
        )
        self.docs = redundant_filter.transform_documents(self.docs)
        self.logger.info(f"{len(self.docs)} publication sections remain in memory")

        return None

    def _split_documents(self):
        """
        Splits documents into chunks
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.split_length,
            chunk_overlap=self.split_overlap,
            length_function=len,
        )

        self.chunks = self.text_splitter.split_documents(self.docs)

        self.logger.info(f"{len(self.chunks)} chunks loaded to memory")
        return None

    def _embed_documents(self):
        """
        Tokenise all document chunks and commit to vector store,
        persisting in local memory for efficiency of reproducibility
        """
        self.temp_db = FAISS.from_documents(self.chunks, self.embeddings)

        return None

    def _merge_faiss_db(self):
        """
        Merge temporary vector store for new publications into
        existing permanent vector store
        """
        db = FAISS.load_local(
            self.faiss_db_root, self.embeddings, allow_dangerous_deserialization=True
        )
        db.merge_from(self.temp_db)
        db.save_local(self.faiss_db_root)
        self.logger.info(
            f"Number of chunks in vector store POST-edit: {len(db.docstore._dict)}"
        )

        return None

    def _cleaning_up(self):
        """
        Move all publications and publication sections from temporary
        folders to permanent; remove temporary folders
        """
        path = f"{self.latest_directory}/*.json"
        all_files = glob.glob(path)
        for FILE in all_files:
            file = FILE.split("\\")[-1]
            dst_path = os.path.join(self.latest_directory, file)
            os.rename(FILE, dst_path)

        path = f"{self.latest_split_directory}/*.json"
        split_files = glob.glob(path)
        for FILE in split_files:
            file = FILE.split("/")[-1]
            dst_path = os.path.join(self.latest_split_directory, file)
            os.rename(FILE, dst_path)

        # remove all temporary files
        shutil.rmtree(self.latest_directory)

        return None


if __name__ == "__main__":
    # define session_id that will be used for log file and feedback
    session_name = f"statschat_updater_{format(datetime.now(), '%Y_%m_%d_%H:%M')}"
    logger = logging.getLogger(__name__)
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_fmt,
        filename=f"log/{session_name}.log",
        filemode="a",
    )
    # initiate Statschat AI and start the app
    config = load_config(name="main")

    prepper = UpdateVectorStore(**config["db"], **config["preprocess_latest"])
    logger.info("Vector store updated...")
    print("update of docstore should be complete.")
