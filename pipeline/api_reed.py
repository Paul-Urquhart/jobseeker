import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os
import json
from app.models import ReedRaw
from app.db import Session
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from pipeline.configure_logging import configure_logging
import logging

configure_logging()
logger = logging.getLogger("api_reed")

load_dotenv()
API_KEY_REED = os.environ.get('API_KEY_REED')


def get_reed_data() -> list[dict]:

    # parameters
    url ='https://www.reed.co.uk/api/1.0/search'
    auth = HTTPBasicAuth(API_KEY_REED, "")
    params = {
        'keywords': 'data engineer',
        'locationName': 'london',
        'postedByDirectEmployer': True,
        'distanceFromLocation': 10,
        'resultsToTake': 100
    }

    # API first contact - get first page up to 100 results (API limit)
    logger.info("contacting api")
    response = requests.get(url, auth=auth, params=params)
    logger.info("no error from api")
    logger.info(f"Status code: {response.status_code}")

    json_data = response.json()

    logger.info(f"{len(json_data['results'])} jobs received.")
    logger.info(f"Total results: {json_data['totalResults']}")

    # API pages loop to get the remaning results
    number_of_calls = json_data['totalResults'] // 100
    logger.info(f"Number of API calls needed: {number_of_calls}")

    for call in range(1, number_of_calls + 1):
        skip = call * 100
        params['resultsToSkip'] = skip
        print(f"API call {call}")
        response = requests.get(url, auth=auth, params=params)
        for job in response.json()['results']:
            json_data['results'].append(job)
        logger.info(f"API call {call} complete. {len(json_data['results'])} results in total.")


    # format jobs to return
    jobs = []
    for job in json_data['results']:
        new_job = {
            "source": "Reed",
            "source_id": str(job["jobId"]),
            "job_title": job["jobTitle"],
            "employer_name": job["employerName"],
            "location": job["locationName"],
            "num_applications": job["applications"],
            "min_salary": job["minimumSalary"],
            "max_salary": job["maximumSalary"],
            "date_posted": datetime.strptime(job["date"], "%d/%m/%Y").date(),
            "date_expires": datetime.strptime(job["expirationDate"], "%d/%m/%Y").date(),
            "job_description": job["jobDescription"],
            "job_url": job["jobUrl"],
        }
        jobs.append(new_job)

    return jobs




jobs = get_reed_data()
print("Count of jobs from Reed with new function is: ", len(jobs))



#     stmt = insert(ReedRaw).values(new_job)
#     stmt = stmt.on_conflict_do_nothing(
#             index_elements=[ReedRaw.id]
#         )

#     return stmt


# logger.info("Committing to database")
# with Session() as db_session:
#     for job in json_data["results"]:
#         stmt = add_job(job)
#         db_session.execute(stmt)
#         db_session.commit()

# logger.info("Ingestion complete from Reed api")
