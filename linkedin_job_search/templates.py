EXTRACT_KEYWORDS_PROMT_TEMPLATE = """
You will be given a job description. You need to analyse the job description completely first step by step
and after that you need to extract TOP 5 IMPORTANT keywords which are essential for this job description.

<Output Format>
Print the final output in comma separated list (NO PREAMBLE). NOTHING ELSE NEEDED IN THE OUTPUT.
</Output Format>

*** YOUR OUTPUT SHOULD COME ONLY FROM THE PROVIDED DATA AND NOTHING ELSE. DO NOT ASSUME ANYTHING FROM YOUR SIDE."

Job Description: {job_description}
"""


GET_CANDIDATES_PROMT_TEMPLATE = [
    (
        "system",
        "Act as a HR of a company who is looking for some candidates to fill a job position",
    ),
    (
        "ai",
        """
            You will be given a job description and some candidates profiles. You first need to analyse the\
            job description step-by-step. After that analyse each job profile. Once all these done\
            then you need to compare each job profile with the job description and then report out 3 potential\
            candidate which is most suitable for the job.\
            
            ###
            The output should contain the candidate name, his years of experience, his job skills and his linkedin profile url, his present company (NO PREAMBLE)
            ###
            
            ***YOUR ANASWER SHOULD COMES FROM THE GIVEN JOB PROFILES ONLY AND NOTHING ELSE.***
            """,
    ),
    (
        "human",
        (
            "Job Description: {job_description} \n\n Candidates Profiles: {candidate_profiles}"
        ),
    ),
]
