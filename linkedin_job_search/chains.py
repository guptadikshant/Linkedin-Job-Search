from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.chat import ChatPromptTemplate

from linkedin_job_search.templates import (
    EXTRACT_KEYWORDS_PROMT_TEMPLATE,
    GET_CANDIDATES_PROMT_TEMPLATE,
)


def extract_relevant_keywords(llm_model, job_description: str, logger) -> list:
    logger.info("Extracting relevant keywords from job description.")
    prompt = ChatPromptTemplate.from_template(EXTRACT_KEYWORDS_PROMT_TEMPLATE)

    chain = prompt | llm_model | StrOutputParser()

    keywords = chain.invoke(job_description)

    keywords_list = keywords.split(", ")

    logger.info(f"Relevant keywords extracted. Keywords: {keywords_list}")

    return keywords_list


def get_relevant_candiates_profiles(
    relevant_docs: list[str], job_description: str, llm_model, logger
) -> str:
    logger.info("Searching relevant candidates profiles.")
    job_search_prompt = ChatPromptTemplate.from_messages(GET_CANDIDATES_PROMT_TEMPLATE)

    # Creating Chain for retrieval
    chain = job_search_prompt | llm_model | StrOutputParser()

    logger.info("Successfully retrieved relevant job profiles.")

    return chain.invoke(
        {"candidate_profiles": relevant_docs, "job_description": job_description}
    )
