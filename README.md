# supportBot
A RAG based support bot written in python, using faiss and tranformers.

# Architecture Overview
    ServiceBot service 
    - Integrates with the embedding service (embedding-generator).
    - Embedding searched across the searcher services (semantic-index-service), which held the faiss index in memory, and returns the potential candidate with a matching score.
    - If score surpasses the theshold, its forwarded for next steps, if not return PRESET RESPONSE.
    - Injects the query asked, relevant info extracted from the faiss, generates answer with a pre-formatted prompt to the question-answering LLM (answer-gen-service) and returns the answer as the response.

# Highlights
    1. Each service entity is compartmentalized i.e isolated, which allows the system to scale easily. 
    2. Indexes are partitioned across the type of doc, i.e pdf and web here from the point of maintainability, which later can be partitioned over the index size.
    3. answer-gen-service is integrated to the controller component of serviceBot, which allows for faster transfer and still can be isolated by deploying it as individual service.
    4. This decoupled architecture allows to add new faiss index services seamless, and further streamlined by integrating a service registry as coordination layer.

# Improvements
    1. Adding a semantic cache logic in the serviceBot controller component itself, by holding a few set of embeddings to it.
    2. Ramping Infra i.e GPU for ML related services for faster turnaround.
    3. Using better ML models, which are more suitable for the use case.
    4. Telemetry, like query latency, embedding throughput to be captured.
    5. Feedback loop for the queries answered.