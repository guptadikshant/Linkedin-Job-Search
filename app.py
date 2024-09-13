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
    format="%(asctime)s - %(levelname)s -  [%(filename)s::%(lineno)d] - %(message)s"
)

def main():
    logger.info("Started the server.")
    st.title("Candidate Search on Linkedin")

    with st.sidebar:
        search_keyword: str = st.text_input("Please enter the job title here.....")
        save_data = st.button("Save Data")
        # job_description: str = st.text_area("Please enter job description here....")

        if search_keyword and save_data:
            logger.info(f"Got the job title: {search_keyword}")
            with st.spinner("Loading Data into ChromaDB"):
                collection_name = "_".join(search_keyword.lower().split(" "))

                try:
                    logger.info("Authenticating to Linkedin")
                    # Authenticate using any Linkedin account credentials
                    api = Linkedin(
                        username=os.environ["LINKEDIN_USERNAME"],
                        password=os.environ["LINKEDIN_PASSWORD"],
                    )
                    logger.info("Successfully authenticated to Linkedin")
                except Exception as err:
                    logger.error(f"Error occurred in authenticating to linkediin. Error: {err}")

                logger.info(f"Searching people with job title {search_keyword}")
                # Search people with the supplied job title
                poeples_with_job_title = api.search_people(
                    keywords=search_keyword, limit=20
                )

                # Converting into a Dataframe for post processing
                all_peoples_df = pd.DataFrame(poeples_with_job_title)

                # Get people profile details and their associated skills
                all_peoples_profiles = create_people_profiles_skills(
                    api=api, all_peoples_df=all_peoples_df, logger=logger
                )

                # Cleaned the data
                cleaned_data = structure_data_for_database(
                    peoples_profiles=all_peoples_profiles, logger=logger
                )

                # Loading data into chroma vector database
                load_data_into_chroma(
                    persist_dir=VECTOR_DATABASE_DIR,
                    collection_name=collection_name,
                    all_documents=cleaned_data,
                    logger=logger
                )
            st.success("Successfully added data into chromadb")


if __name__ == "__main__":
    main()
