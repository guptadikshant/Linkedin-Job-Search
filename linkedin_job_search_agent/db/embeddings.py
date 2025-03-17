import os
from typing import List

import google.generativeai as gemini_client
from google.generativeai.embedding import embed_content
# from sentence_transformers import SentenceTransformer


class VectorEmbeddings:
    """
    Class to handle embedding generation using different APIs.
    Currently supports Gemini and SentenceTransformers.
    """

    def __init__(self, model_id: str) -> None:
        gemini_client.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_id = model_id
        # Initialize sentence transformer model if needed
        # if not model_id.startswith("models/"):
        #     self.sentence_model = SentenceTransformer(model_id)

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings using either Gemini or SentenceTransformers based on model_id.
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding vectors or empty list if error occurs
        """
        # Determine which API to use based on model_id prefix
        if self.model_id.startswith("models/"):
            return self._gemini_embedding(text)
        # else:
        #     return self._sentence_transformer_embedding(text)

    def _gemini_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings using Gemini API.
        """
        try:
            response = embed_content(content=text, model=self.model_id)
            return response["embedding"]

        except Exception as e:
            print(f"Error generating Gemini embedding: {e}")
            return []

    # def _sentence_transformer_embedding(self, text: str) -> List[float]:
    #     """
    #     Generate embeddings using SentenceTransformers.
    #     """
    #     try:
    #         embedding = self.sentence_model.encode(text)
    #         return embedding.tolist()

    #     except Exception as e:
    #         print(f"Error generating SentenceTransformer embedding: {e}")
    #         return []
