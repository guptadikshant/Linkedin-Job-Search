import logging
import os

import pandas as pd
import streamlit as st
from dotenv import find_dotenv, load_dotenv
from linkedin_api import Linkedin

from linkedin_job_search.chains import extract_relevant_keywords, get_relevant_candiates_profiles
from linkedin_job_search.constants import (
    GROQ_MODEL,
    GROQ_MODEL_TEMPERATURE,
    VECTOR_DATABASE_DIR,
)
from linkedin_job_search.data_processing import (
    create_people_profiles_skills,
    structure_data_for_database,
)
from linkedin_job_search.database import load_data_from_chroma, load_data_into_chroma
from linkedin_job_search.models import LLMModel

# loading env variables
load_dotenv(find_dotenv())

logger = logging.getLogger()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s -  [%(filename)s::%(lineno)d] - %(message)s",
)


def main():
    logger.info("Started the server.")
    st.title("Candidate Search on Linkedin")

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
                            )
                            logger.info("Successfully authenticated to Linkedin")
                        except Exception as err:
                            logger.error(
                                f"Error occurred in authenticating to Linkedin. Error: {err}"
                            )
                            return

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

    logger.info(f"Data loaded Session State: {st.session_state.data_loaded}")

    if st.session_state.data_loaded:
        job_desciption = st.text_area("Please enter the job description here....")

        get_data = st.button("Get Response")

        if job_desciption and get_data:
            llm_model = LLMModel().get_groq_model(
                model_name=GROQ_MODEL, temperature=GROQ_MODEL_TEMPERATURE, logger=logger
            )
            relevant_job_keywords = extract_relevant_keywords(
                llm_model=llm_model, job_description=job_desciption, logger=logger
            )

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
                logger=logger
            )

            st.write(job_profiles)

        # Button to reset the keyword and start a new search
        if st.button("Enter new keyword"):
            st.session_state.data_loaded = False  # Reset the flag to allow a new search
            st.session_state.search_keyword = None
            st.session_state.collection_name = None


if __name__ == "__main__":
    main()
