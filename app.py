import logging
import os

import pandas as pd
import streamlit as st
from dotenv import find_dotenv, load_dotenv
from linkedin_api import Linkedin

from linkedin_job_search_agent.chains import (
    extract_relevant_keywords,
    get_relevant_candiates_profiles,
)
from linkedin_job_search_agent.constants import (
    GEMINI_MODEL,
    GEMINI_MODEL_TEMPERATURE,
    VECTOR_DATABASE_DIR,
)
from linkedin_job_search_agent.data_processing import (
    create_people_profiles_skills,
    structure_data_for_database,
)
from linkedin_job_search_agent.database import (
    load_data_from_chroma,
    load_data_into_chroma,
)
from linkedin_job_search_agent.models import LLMModel

# loading env variables
load_dotenv(find_dotenv())

logger = logging.getLogger()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s -  [%(filename)s::%(lineno)d] - %(message)s",
)


def main():
    logger.info("Started the server.")
    st.title("AI Based Candidate Search on Linkedin")

    # Initialize session state if not already set
    if "collection_name" not in st.session_state:
        st.session_state.collection_name = None
    if "search_keyword" not in st.session_state:
        st.session_state.search_keyword = None
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False  # Flag to track data loading

    with st.container():
        if not st.session_state.data_loaded:
            with st.sidebar:
                search_keyword: str = st.text_input(
                    "Please enter the job title here....."
                )
                save_data = st.button("Save Data")

                # Update the collection_name if a new search_keyword is entered
                if search_keyword != st.session_state.search_keyword and save_data:
                    st.session_state.search_keyword = search_keyword
                    logger.info(
                        f"User enter's job title: {st.session_state.search_keyword}"
                    )

                    st.session_state.collection_name = "_".join(
                        search_keyword.lower().split(" ")
                    )
                    logger.info(f"Collection name: {st.session_state.collection_name}")

                    with st.spinner("Loading Data into ChromaDB"):
                        try:
                            logger.info("Authenticating to Linkedin")
                            # Authenticate using any Linkedin account credentials
                            api = Linkedin(
                                username=os.environ["LINKEDIN_USERNAME"],
                                password=os.environ["LINKEDIN_PASSWORD"],
                                refresh_cookies=True,
                            )
                            logger.info("Successfully authenticated to Linkedin")

                            logger.info(
                                f"Searching people with job title {st.session_state.search_keyword}"
                            )
                            poeples_with_job_title = api.search_people(
                                keywords=st.session_state.search_keyword, limit=20
                            )

                            all_peoples_df = pd.DataFrame(poeples_with_job_title)

                            all_peoples_profiles = create_people_profiles_skills(
                                api=api, all_peoples_df=all_peoples_df, logger=logger
                            )

                            cleaned_data = structure_data_for_database(
                                peoples_profiles=all_peoples_profiles, logger=logger
                            )

                            load_data_into_chroma(
                                persist_dir=VECTOR_DATABASE_DIR,
                                collection_name=st.session_state.collection_name,
                                all_documents=cleaned_data,
                                logger=logger,
                            )
                            st.session_state.data_loaded = True
                            st.success("Successfully added data into ChromaDB")

                        except Exception as err:
                            if "CHALLENGE" in str(err):
                                logger.error(
                                    f"LinkedIn security challenge detected. Error: {err}"
                                )
                                st.error(
                                    "LinkedIn has blocked the authentication attempt with a security challenge. "
                                    "This typically happens when:\n"
                                    "1. The account needs to complete a verification step\n"
                                    "2. LinkedIn has detected automated login attempts\n\n"
                                    "Please try:\n"
                                    "- Logging into your LinkedIn account manually in a browser\n"
                                    "- Complete any security verifications\n"
                                    "- Check that your credentials are correct in the .env file"
                                )
                            else:
                                logger.error(
                                    f"Error occurred in authenticating to LinkedIn. Error: {err}"
                                )
                                st.error(f"Authentication error: {str(err)}")

                            # Check if we have existing data for this collection
                            try:
                                from chromadb import PersistentClient

                                client = PersistentClient(path=VECTOR_DATABASE_DIR)
                                collections = client.list_collections()
                                if st.session_state.collection_name in [
                                    c.name for c in collections
                                ]:
                                    if st.button(
                                        "Use previously cached data for this job title"
                                    ):
                                        st.session_state.data_loaded = True
                                        st.warning(
                                            "Using previously cached data for this job title"
                                        )
                            except Exception as db_err:
                                logger.error(
                                    f"Failed to check for existing collection: {db_err}"
                                )

    if st.session_state.data_loaded:
        job_desciption = st.text_area("Please enter the job description here....")

        get_data = st.button("Get Response")

        if job_desciption and get_data:
            with st.spinner("Getting Relevant Job Profiles"):
                # llm_model = LLMModel().get_groq_model(
                #     model_name=GROQ_MODEL,
                #     temperature=GROQ_MODEL_TEMPERATURE,
                #     logger=logger,
                # )
                llm_model = LLMModel().get_gemini_model(
                    model_name=GEMINI_MODEL,
                    temperature=GEMINI_MODEL_TEMPERATURE,
                    logger=logger,
                )
                relevant_job_keywords = extract_relevant_keywords(
                    llm_model=llm_model, job_description=job_desciption, logger=logger
                )

                try:
                    retrieved_relevant_docs = load_data_from_chroma(
                        persist_dir=VECTOR_DATABASE_DIR,
                        collection_name=st.session_state.collection_name,
                        job_description=job_desciption,
                        relevant_keywords=relevant_job_keywords,
                        logger=logger,
                    )

                    job_profiles = get_relevant_candiates_profiles(
                        relevant_docs=retrieved_relevant_docs,
                        job_description=job_desciption,
                        llm_model=llm_model,
                        logger=logger,
                    )

                    st.write(job_profiles)
                except Exception as e:
                    logger.error(f"Error retrieving data: {e}")
                    st.error(f"Failed to retrieve candidate profiles: {str(e)}")

        # Button to reset the keyword and start a new search
        if st.button("Enter new job title"):
            st.session_state.data_loaded = False  # Reset the flag to allow a new search
            st.session_state.search_keyword = None
            st.session_state.collection_name = None


if __name__ == "__main__":
    main()
