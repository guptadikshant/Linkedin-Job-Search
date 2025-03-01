import os
from typing import List

import chromadb
from chromadb.utils.embedding_functions.openai_embedding_function import (
    OpenAIEmbeddingFunction,
)


def load_data_into_chroma(
    persist_dir: str, collection_name: str, all_documents: List[List], logger
):
    try:
        logger.info("Loading data into chromadb.")
        # client creation
        client = chromadb.PersistentClient(path=persist_dir)
        collection = client.create_collection(
            name=collection_name,
            embedding_function=OpenAIEmbeddingFunction(
                api_key=os.environ["OPENAI_API_KEY"]
            ),
        )

        # Saving each person's profile into chromadb
        for doc in all_documents:
            try:
                collection.add(
                    ids=doc.id,
                    documents=doc.page_content,
                    metadatas=doc.metadata,
                )
            except Exception:
                continue
    except Exception as err:
        logger.error(f"Error occurred in loading data into chroma. Error: {err}")


def load_data_from_chroma(
    persist_dir: str, collection_name: str, job_description, relevant_keywords, logger
):
    logger.info("Retrieving relevant documents")
    client = chromadb.PersistentClient(path=persist_dir)

    collection = client.get_collection(
        name=collection_name,
        embedding_function=OpenAIEmbeddingFunction(
            api_key=os.environ["OPENAI_API_KEY"]
        ),
    )

    retrieved_documents = collection.query(
        query_texts=job_description,
        n_results=8,
        include=["documents"],
        where={
            "$or": [
                {relevant_keywords[0]: relevant_keywords[0]},
                {relevant_keywords[1]: relevant_keywords[1]},
                {relevant_keywords[2]: relevant_keywords[2]},
                {relevant_keywords[3]: relevant_keywords[3]},
                {relevant_keywords[4]: relevant_keywords[4]},
            ]
        },
    )["documents"]

    logger.info(f"Retrieved {len(retrieved_documents[0])} documents.")

    return retrieved_documents
