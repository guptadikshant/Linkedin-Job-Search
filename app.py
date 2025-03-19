from loguru import logger
import sys
import streamlit as st
from dotenv import find_dotenv, load_dotenv
from linkedin_job_search_agent.db.vector_store import QdrantVectorStore
from linkedin_job_search_agent.model.chains import (
    extract_relevant_keywords,
    get_relevant_candiates_profiles,
)
from linkedin_job_search_agent.utils import load_yaml
from linkedin_job_search_agent.model.models import LLMModel

# loading env variables
load_dotenv(find_dotenv())

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)
# for adding logs into a log file
# logger.add(
#     "app.log",
#     rotation="500 MB",
#     level="INFO",
#     format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
# )


@st.cache_data
def load_config():
    """
    Load the configuration file for the application.
    Returns:
        dict: Configuration settings loaded from the YAML file.
    """
    try:
        config = load_yaml("linkedin_job_search_agent/config.yml")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return None


def main():
    """
    Main function to run the LinkedIn Job Search Agent application.
    """

    logger.info("Starting LinkedIn Job Search Agent application.")

    st.title("LinkedIn Job Search Agent")
    st.subheader("Find the best candidates for your job description")

    job_description = st.text_area("Enter Job Description", height=300)

    job_title = st.text_input("Enter Job Title to Search For")

    if st.button("Search Profiles"):
        config_data = load_config()
        with st.spinner("Getting Relevant Job Profiles"):
            if config_data:
                llm_model = LLMModel().get_gemini_model(
                    model_name=config_data["configurations"]["llm_model_config"][
                        "gemini_model"
                    ]["model_id"],
                    temperature=config_data["configurations"]["llm_model_config"][
                        "gemini_model"
                    ]["temperature"],
                )

                relevant_job_keywords = extract_relevant_keywords(
                    llm_model=llm_model, job_description=job_description
                )

                vector_store = QdrantVectorStore(
                    collection_name=config_data["configurations"][
                        "vector_database_config"
                    ]["collection_name"],
                    embedding_model_id=config_data["configurations"][
                        "embedding_model_config"
                    ]["gemini_embedding_model"]["model_id"],
                    embedding_model_type="gemini",
                )

                # Load data from Qdrant
                relevant_profiles = vector_store.load_data_from_qdrant(
                    job_description=job_description,
                    relevant_keywords=relevant_job_keywords,
                    limit=10,
                    searched_job_title=job_title,
                )

                st.write_stream(
                    get_relevant_candiates_profiles(
                        relevant_docs=relevant_profiles,
                        job_description=job_description,
                        llm_model=llm_model,
                    )
                )


if __name__ == "__main__":
    main()
