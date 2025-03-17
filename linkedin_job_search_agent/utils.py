import yaml
from loguru import logger

def load_yaml(file_path: str) -> dict:
    """Load a YAML file and return its content as a dictionary."""
    try:
        logger.info(f"Loading YAML file from {file_path}.")
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        logger.info("YAML file loaded successfully.")
        return data
    except Exception as e:
        logger.error(f"Error loading YAML file: {e}")
        return None