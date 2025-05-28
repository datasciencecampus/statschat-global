### Search & response parameters

There are some key parameters in `statschat/config/main.toml` that we're
experimenting with to improve the search results, and the generated text
answer.  The current values are initial guesses:

| Parameter | Current Value | Function |
| --- | --- | --- |
| k_contexts | 3 | Number of top documents to pass to generative QA LLM |
| k_docs | 10 | Maximum number of search results to return |
| answer_threshold | 0.5 | Threshold score below which a answer is returned in a search |
| document_threshold| 0.9 | Threshold score below which a document is returned in a search |
| similarity_threshold | 2.0 | Cosine distance, a searched document is only returned if it is at least this similar (EQUAL or LOWER) |
