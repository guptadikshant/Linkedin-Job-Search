import os
from typing import List
import chromadb
from chromadb.utils.embedding_functions.openai_embedding_function import (
    OpenAIEmbeddingFunction,
)


def load_data_into_chroma(persist_dir: str, collection_name: str, all_documents: List[List]):
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




def load_data_from_chroma():
    pass