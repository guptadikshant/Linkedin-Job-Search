from linkedin_job_search_agent.utils import load_yaml
from linkedin_job_search_agent.db.vector_store import QdrantVectorStore
from linkedin_job_search_agent.core.profiles_data import get_profile_data
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s -  [%(filename)s::%(lineno)d] - %(message)s",
)

logger = logging.getLogger()

def etl_main():
    try:
        # Load configuration
        start_time = time.perf_counter()
        config = load_yaml("linkedin_job_search_agent\config.yml")
        # get all the profiles data
        profile_data = get_profile_data(job_title="Software Engineer")
        # intialize the vector store
        vector_store = QdrantVectorStore(
            collection_name=config["configurations"]["vector_database_config"]["collection_name"],
        )
        # load the data into qdrant
        vector_store.load_data_into_qdrant(
            all_documents=profile_data,
            vector_size=config["configurations"]["embdding_model_config"]["gemini_embedding_model"]["dimension"],
            embedding_model_id=config["configurations"]["embdding_model_config"]["gemini_embedding_model"]["model_id"],
            embedding_model_type="gemini",
        )
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        logger.info(f"Configuration loaded in {elapsed_time:.2f} seconds.")
    except Exception as e:
        logger.error(f"Error in ETL process: {e}")

if __name__ == "__main__":

    etl_main()