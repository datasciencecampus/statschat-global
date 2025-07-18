# Configuration Parameters Explained

Below is an explanation of each configuration parameter found in the TOML file:

## [db]

- **faiss_db_root**: Path to the FAISS vector database directory used for storing embeddings.
- **embedding_model_name**: Name of the sentence embedding model to use. Alternatives are listed in the comments.

## [preprocess]

- **download_mode**: Determines whether to set up or update the dataset. Options: `"SETUP"` or `"UPDATE"`.
- **download_site**: URL to download PDFs from. Leave empty if PDFs are added manually to `data/pdf_store`.
- **data_dir**: Directory where processed data is stored.
- **download_dir**: Directory where downloaded PDFs are saved.
- **directory**: Directory for storing JSON conversions of the PDFs.
- **split_directory**: Directory for storing split JSON files.
- **split_length**: Number of characters per text chunk when splitting documents.
- **split_overlap**: Number of overlapping characters between chunks.
- **latest_only**: If `true`, only the latest documents are processed.

## [search]

- **generative_model_name**: Name of the generative language model used for answering queries. Alternatives are listed in the comments.
- **k_docs**: Number of top documents to retrieve per search.
- **k_contexts**: Number of context chunks to use for generating answers.
- **similarity_threshold**: Minimum similarity score required for a document to be considered relevant in search results.
- **llm_temperature**: Sampling temperature for the language model (controls randomness).
- **answer_threshold**: Minimum score required for an answer to be returned.
- **document_threshold**: Minimum score required for a document to be included in results.

## [app]

- **latest_max**: Maximum number of latest documents to consider. Common values are 0, 1, or 2.
- **page_start**: Sets where to start looking for downloads. Higher the number the older the publications.
- **page_end**: Sets where to stop looking for downloads. Higher the number the older the publications.

---
