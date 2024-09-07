import json
import time
import os
from linkedin_api import Linkedin
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Authenticate using any Linkedin account credentials
api = Linkedin(
    username=os.environ["LINKEDIN_USERNAME"],
    password=os.environ["LINKEDIN_PASSWORD"]
)

# GET a profile
profile = api.get_profile(urn_id="ACoAAAZZciMBmlehJoR3zG5AnILlz_0LDgRmano")

# profile_skills = api.get_profile_skills(public_id="dikshant-gupta-9a7083170")

print(profile["skills"])

# # with open("profile_response.json", "w") as file:
# #     json.dump(profile, file)

# start_time = time.time()

# all_people_list = api.search_people(
#     keywords="Data Scientist", limit=20
# )

# with open("datascientist_list.json", "w") as file:
#     json.dump(all_people_list, file)

# end_time = time.time()

# print(f"total time taken: {end_time - start_time}")