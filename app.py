import os
import streamlit as st
import pandas as pd
from linkedin_api import Linkedin
from dotenv import load_dotenv, find_dotenv
import logging

from linkedin_job_search.constants import VECTOR_DATABASE_DIR
from linkedin_job_search.data_processing import (
    create_people_profiles_skills,
    structure_data_for_database,
)
from linkedin_job_search.database import load_data_into_chroma

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

    with st.sidebar:
        search_keyword: str = st.text_input("Please enter the job title here.....")
        save_data = st.button("Save Data")

        # Update the collection_name if a new search_keyword is entered
        if search_keyword != st.session_state.search_keyword and save_data:
            st.session_state.search_keyword = search_keyword
            logger.info(f"User enter's job title: {st.session_state.search_keyword}")

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
            st.success("Successfully added data into ChromaDB")


if __name__ == "__main__":
    main()
