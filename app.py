import logging

import streamlit as st
from dotenv import find_dotenv, load_dotenv


# loading env variables
load_dotenv(find_dotenv())

logger = logging.getLogger()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s -  [%(filename)s::%(lineno)d] - %(message)s",
)


def main():
    """
    Main function to run the LinkedIn Job Search Agent application.
    """

    logger.info("Starting LinkedIn Job Search Agent application.")

    st.title("LinkedIn Job Search Agent")
    st.subheader("Find the best candidates for your job description")

    job_description = st.text_area("Enter Job Description", height=300)

    if job_description:
        pass


if __name__ == "__main__":
    main()