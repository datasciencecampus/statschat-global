### Search engine parameters

There are some key parameters in `statschat/_config/main.toml` that we're
experimenting with to improve the search results, and the generated text
answer.  The current values are initial guesses:

| Parameter | Current Value | Function |
| --- | --- | --- |
| k_docs | 10 | Maximum number of search results to return |
| similarity_threshold | 2.0 | Cosine distance, a searched document is only returned if it is at least this similar (EQUAL or LOWER) |
| k_contexts | 3 | Number of top documents to pass to generative QA LLM |
