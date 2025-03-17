import logging
import os
from linkedin_api import Linkedin
import pandas as pd
from linkedin_job_search_agent.preprocessing.data_processing import (
    create_people_profiles_skills,
    structure_data_for_database,
)

logger = logging.getLogger()


def get_profile_data(job_title: str, limit: int) -> dict:
    """
    Fetches LinkedIn profiles based on the job title and structures the data for database insertion."
    Args:
        job_title (str): The job title to search for on LinkedIn.
    Returns:
        dict: Structured data containing LinkedIn profiles and their skills.
    """
    try:
        logger.info(f"Fetching LinkedIn profiles for job title: {job_title}")
        # Initialize LinkedIn API client
        linkedin_api = Linkedin(
            username=os.getenv("LINKEDIN_USERNAME"),
            password=os.getenv("LINKEDIN_PASSWORD"),
        )
        # Fetch profiles from LinkedIn
        profiles = linkedin_api.search_people(
            keywords=job_title,
            limit=limit,
        )

        all_peoples_df = pd.DataFrame(profiles)

        # Create people profiles skills
        all_peoples_profiles = create_people_profiles_skills(
            api=linkedin_api, all_peoples_df=all_peoples_df
        )

        # Structure data for database
        structured_data = structure_data_for_database(
            peoples_profiles=all_peoples_profiles, job_title=job_title
        )
        logger.info(f"Fetched: {len(structured_data)} profiles")

        return structured_data
    except Exception as e:
        logger.error(f"Error fetching LinkedIn profiles: {e}")
        return {}
