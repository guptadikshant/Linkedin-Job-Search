import os
import logging
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_groq.chat_models import ChatGroq

logger = logging.getLogger()

class LLMModel:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_gemini_model(
        model_name: str, temperature: int
    ) -> ChatGoogleGenerativeAI:
        logger.info(
            f"Getting {model_name} gemini model with temperature: {temperature}"
        )
        gemini_model = ChatGoogleGenerativeAI(
            api_key=os.environ["GOOGLE_API_KEY"],
            model=model_name,
            temperature=temperature,
        )
        logger.info(
            f"Successfully get {model_name} gemini model with temperature: {temperature}"
        )
        return gemini_model

    @staticmethod
    def get_groq_model(model_name: str, temperature: str) -> ChatGroq:
        logger.info(f"Getting {model_name} groq model with temperature: {temperature}")
        groq_model = ChatGroq(
            api_key=os.environ["GROQ_API_KEY"],
            model=model_name,
            temperature=temperature,
        )
        logger.info(
            f"Successfully get {model_name} groq model with temperature: {temperature}"
        )
        return groq_model
