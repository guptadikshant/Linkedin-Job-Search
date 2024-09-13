from collections import defaultdict
import json
import pandas as pd
from langchain_core.documents import Document


def create_people_profiles_skills(api, all_peoples_df: pd.DataFrame, logger):
    try:
        logger.info("Getting people's profile and skills.")
        people_urn_ids = []
        for _, col in all_peoples_df.iterrows():
            people_urn_ids.append(col["urn_id"])

        peoples_profiles: dict[str, list] = defaultdict(list)

        for urn_id in people_urn_ids:
            try:
                profile_details = api.get_profile(urn_id=urn_id)
                skills = api.get_profile_skills(urn_id=urn_id)
                peoples_profiles[urn_id].append(
                    {"profile_details": profile_details, "skills": skills}
                )
            except KeyError:
                continue
        logger.info("Successfully got all the people's profile and skills")
        return peoples_profiles
    
    except Exception as err:
        logger.error(f"Error occurred in getting people's profile and data. Error: {err}")




def data_cleanup(peoples_profiles: pd.DataFrame, logger):
    try:
        logger.info("Started cleaning up the data.")
        # code to clean up unnecessary details
        for _, values in peoples_profiles.items():
            for val in values:
                for _, v1 in val.items():
                    if isinstance(v1, dict):
                        if "student" in v1:
                            del v1["student"]
                        if "geoCountryUrn" in v1:
                            del v1["geoCountryUrn"]
                        if "geoLocationBackfilled" in v1:
                            del v1["geoLocationBackfilled"]
                        if "entityUrn" in v1:
                            del v1["entityUrn"]
                        if "geoCountryName" in v1:
                            del v1["geoCountryName"]
                        if "elt" in v1:
                            del v1["elt"]
                        if "profilePictureOriginalImage" in v1:
                            del v1["profilePictureOriginalImage"]
                        if "industryUrn" in v1:
                            del v1["industryUrn"]
                        if "profilePicture" in v1:
                            del v1["profilePicture"]
                        if "geoLocation" in v1:
                            del v1["geoLocation"]
                        if "geoLocationName" in v1:
                            del v1["geoLocationName"]
                        if "location" in v1:
                            del v1["location"]
                        if "backgroundPicture" in v1:
                            del v1["backgroundPicture"]
                        if "backgroundPictureOriginalImage" in v1:
                            del v1["backgroundPictureOriginalImage"]
                        if "displayPictureUrl" in v1:
                            del v1["displayPictureUrl"]
                        if "img_400_400" in v1:
                            del v1["img_400_400"]
                        if "img_200_200" in v1:
                            del v1["img_200_200"]
                        if "img_800_800" in v1:
                            del v1["img_800_800"]
                        if "img_100_100" in v1:
                            del v1["img_100_100"]
                        if "img_767_767" in v1:
                            del v1["img_767_767"]
                        if "profile_id" in v1:
                            del v1["profile_id"]
                        if "profile_urn" in v1:
                            del v1["profile_urn"]
                        if "member_urn" in v1:
                            del v1["member_urn"]
                        if "volunteer" in v1:
                            del v1["volunteer"]
                        if "honors" in v1:
                            del v1["honors"]
                        if "experience" in v1:
                            for ele in v1["experience"]:
                                if "entityUrn" in ele:
                                    del ele["entityUrn"]
                                if "geoUrn" in ele:
                                    del ele["geoUrn"]
                                if "region" in ele:
                                    del ele["region"]
                                if "companyUrn" in ele:
                                    del ele["companyUrn"]
                                if "companyLogoUrl" in ele:
                                    del ele["companyLogoUrl"]
                        if "education" in v1:
                            for ele in v1["education"]:
                                if "entityUrn" in ele:
                                    del ele["entityUrn"]
                                for sch in ele.get("school", []):
                                    if "objectUrn" in ele:
                                        del ele["objectUrn"]
                                    if "entityUrn" in ele:
                                        del ele["entityUrn"]
                                    if "trackingId" in ele:
                                        del ele["trackingId"]
                                    if "logoUrl" in ele:
                                        del ele["logoUrl"]
                                    if "schoolUrn" in ele:
                                        del ele["schoolUrn"]
                        if "certifications" in v1:
                            for ele in v1["certifications"]:
                                if "company" in ele:
                                    del ele["company"]
                                if "displaySource" in ele:
                                    del ele["displaySource"]
                                if "companyUrn" in ele:
                                    del ele["companyUrn"]
                                if "url" in ele:
                                    del ele["url"]
                        if "projects" in v1:
                            for ele in v1["projects"]:
                                if "members" in ele:
                                    del ele["members"]

        return peoples_profiles
    except Exception as err:
        logger.error(f"Error occurred in cleaning up the data. Error: {err}")


def structure_data_for_database(peoples_profiles: pd.DataFrame, logger):
    try:
        logger.info("Structuring Data for loading data into database.")
        peoples_profiles = data_cleanup(peoples_profiles, logger)

        metadatas = []
        all_documents = []
        for urn_id, profile_info in peoples_profiles.items():
            for info in profile_info:
                metadatas = {}
                documents_without_skills = {
                    k1: v1
                    for k, v in info.items()
                    if k == "profile_details"
                    for k1, v1 in v.items()
                    if k1 != "skills"
                }
                for skill_name in info["skills"]:
                    if "name" in skill_name:
                        metadatas.update({skill_name["name"]: skill_name["name"]})

            all_documents.append(
                Document(
                    page_content=json.dumps(documents_without_skills),
                    metadata=metadatas,
                    id=urn_id,
                )
            )

        return all_documents
    except Exception as err:
        logger.error(f"Error occurred in structuring of the data. Error:{err}")
