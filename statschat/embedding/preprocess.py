import glob
import json
import logging
import toml
import os
from pathlib import Path
from datetime import datetime
from langchain_community.document_loaders import DirectoryLoader, JSONLoader
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_transformers import EmbeddingsRedundantFilter


class PrepareVectorStore(DirectoryLoader, JSONLoader):
    """
    Leveraging Langchain classes to split pre-scraped article
    JSONs to section-level JSONs and loading to document
    store
    """

    def __init__(
        self,
        data_dir: Path = "data/",
        directory: Path = "json_conversions",
        split_directory: Path = "json_split",
        download_dir: Path = "pdf_downloads",
        split_length: int = 1000,
        split_overlap: int = 200,
        embedding_model_name: str = "sentence-transformers/all-mpnet-base-v2",
        redundant_similarity_threshold: float = 0.99,
        faiss_db_root: str = "db_langchain",
        db=None,  # vector store
        logger: logging.Logger = None,
        latest_only: bool = False,
        mode: str = "SETUP",
    ):
        self.directory = data_dir + ("latest_" if mode == "UPDATE" else "") + directory
        self.split_directory = (
            data_dir + ("latest_" if mode == "UPDATE" else "") + split_directory
        )
        self.download_dir = data_dir + download_dir
        self.split_length = split_length
        self.split_overlap = split_overlap
        self.embedding_model_name = embedding_model_name
        self.redundant_similarity_threshold = redundant_similarity_threshold
        self.faiss_db_root = (
            data_dir + faiss_db_root + ("_latest" if mode == "UPDATE" else "")
        )
        # Remove '_latest' from faiss_db_root if present
        self.original_faiss_db_root = (data_dir + faiss_db_root).replace("_latest", "")
        self.db = db
        self.latest_only = latest_only
        self.mode = mode

        # Initialise logger
        if logger is None:
            self.logger = logging.getLogger(__name__)

        else:
            self.logger = logger

        # Create directory for vector store
        if not os.path.exists(self.faiss_db_root):
            os.makedirs(self.faiss_db_root)

        self.logger.info("Split full article JSONs into sections")
        self._json_splitter()
        self.logger.info("Load section JSONs to memory")
        self._load_json_to_memory()
        self.logger.info("Chunk documents")
        self._split_documents()
        self.logger.info("Remove duplicate sections")
        self.remove_duplicate_splits()
        self.logger.info("Instantiate embeddings")
        self._instantiate_embeddings()
        self.logger.info("Filtering out duplicate docs")
        # self._drop_redundant_documents()
        self.logger.info("Vectorise docs and commit to physical vector store")
        self._embed_documents()
        if mode == "UPDATE":
            self.logger.info("Merging vector store with existing data")
            self._merge_faiss_db()

        # except Exception as e:
        #     print(e)
        #     self.logger.error(f"Error in vector store preparation: {e}")

        return None

    def _json_splitter(self):
        """
        Splits scraped json to multiple json,
        one for each article section
        """

        print("Splitting json conversions. Please wait...")

        # create storage folder for split articles
        isExist = os.path.exists(self.split_directory)
        if not isExist:
            os.makedirs(self.split_directory)
        found_articles = glob.glob(f"{self.directory}/*.json")
        self.logger.info(f"Found {len(found_articles)} articles for splitting")
        print(f"Found {len(found_articles)} articles for splitting, please wait..")

        # extract metadata from each article section
        # and store as separate JSON
        for filename in found_articles:
            try:
                with open(filename) as file:
                    json_file = json.load(file)
                    if (not (self.latest_only)) or json_file["latest"]:
                        id = json_file["id"]

                        publication_meta = {
                            i: json_file[i] for i in json_file if i != "content"
                        }
                        for num, section in enumerate(json_file["content"]):
                            section_json = {**section, **publication_meta}

                            # Check that there's text extracted for this section
                            if len(section["page_text"]) > 5:
                                with open(
                                    f"{self.split_directory}/{id}_{num}.json", "w"
                                ) as new_file:
                                    json.dump(section_json, new_file, indent=4)

            except KeyError as e:
                self.logger.warning(f"Could not parse {filename}: {e}")

        return None

    def _load_json_to_memory(self):
        """
        Loads article section JSONs to memory
        """

        print("Loading to memory. Please wait...")

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
        self.logger.info(f"Loading data from {self.split_directory}")
        self.loader = DirectoryLoader(
            self.split_directory,
            glob="*.json",
            use_multithreading=True,
            show_progress=False,
            loader_cls=JSONLoader,
            loader_kwargs=json_loader_kwargs,
        )

        self.docs = self.loader.load()
        self.logger.info(f"{len(self.docs)} article sections loaded to memory")
        return None

    def _instantiate_embeddings(self):
        """
        Loads embedding model to memory
        """

        print("Instantiating embeddings. Please wait...")

        if self.embedding_model_name == "textembedding-gecko@001":
            model = "sentence-transformers/all-mpnet-base-v2"
            self.embeddings = HuggingFaceEmbeddings(model_name=model)
        else:
            model = "sentence-transformers/all-mpnet-base-v2"
            self.embeddings = HuggingFaceEmbeddings(model_name=model)

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
        self.logger.info(f"{len(self.docs)} article sections remain in memory")
        self.logger.info([x.metadata["page_url"] for x in self.docs])

        return None

    def _split_documents(self):
        """
        Splits documents into chunks
        """

        print("Splitting documents into chunks. Please wait...")

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

        print("Embedding documents chunks. Please wait...")

        self.logger.info("Starting embedding of document chunks")
        print("Starting embedding of document chunks, please wait...")

        # Save to FAISS vector store
        self.db = FAISS.from_documents(self.chunks, self.embeddings)
        print("Exporting to FAISS vector store...")
        self.db.save_local(self.faiss_db_root)
        self.logger.info(f"Vector store saved to {self.faiss_db_root}")
        print(f"Vector store saved to {self.faiss_db_root}")

        return None

    def _merge_faiss_db(self):
        """
        Merge temporary vector store for new articles into
        existing permanent vector store
        """

        print("Merging vector store. Please wait...")

        # Load both vector stores as FAISS objects
        db = FAISS.load_local(
            self.original_faiss_db_root,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )
        existing_ids = set(db.docstore._dict.keys())
        filtered_docs = [
            doc
            for doc in self.db.docstore._dict.values()
            if doc.metadata["source"] not in existing_ids
        ]

        print(len(filtered_docs), len(existing_ids))

        db.merge_from(self.db)  # Pass the FAISS object, not the path
        db.save_local(self.faiss_db_root)
        self.logger.info(
            f"Number of chunks in vector store POST-edit: {len(db.docstore._dict)}"
        )

        return None

    def remove_duplicate_splits(self):
        """
        Compares JSON split files in the main and latest split directories.
        Removes any files from the latest split directory that also exist in the
        main split directory.
        """
        # Determine the main split directory (without 'latest_' prefix)
        if "latest_" in self.split_directory:
            main_split_directory = self.split_directory.replace("latest_", "")
        else:
            print("No 'latest_' prefix in split_directory. Skipping duplicate removal.")
            return

        # Get sets of filenames in both directories
        main_files = set(os.listdir(main_split_directory))
        latest_files = set(os.listdir(self.split_directory))

        # Find duplicates
        duplicates = latest_files.intersection(main_files)

        if not duplicates:
            print("No duplicate split files found.")
            return

        print(
            f"Found {len(duplicates)} duplicate split files."
            " Removing from latest split directory..."
        )

        # Remove duplicates from latest split directory
        for filename in duplicates:
            file_path = os.path.join(self.split_directory, filename)
            try:
                os.remove(file_path)
                print(f"Removed duplicate: {file_path}")
            except Exception as e:
                print(f"Failed to remove {file_path}: {e}")

        print("Duplicate removal complete.")


if __name__ == "__main__":
    # define session_id that will be used for log file and feedback
    session_name = f"statschat_preprocess_{format(datetime.now(), '%Y_%m_%d_%H:%M')}"
    logger = logging.getLogger(__name__)
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_fmt,
        filename=f"log/{session_name}.log",
        filemode="a",
    )

    # load config file
    config_path = Path(__file__).resolve().parent.parent / "_config" / "main.toml"
    config = toml.load(config_path)

    prepper = PrepareVectorStore(**config["db"], **config["preprocess"])
    logger.info("setup of docstore should be complete.")
    print("setup of docstore should be complete.")
