# This file currently writes to the same table as Greenhouse. The pipeline will be refactored so all jobs that pass the 
# initial filters will be standarised and saved to the same table.


import requests
import json
from app.models import GreenhouseRaw # change
from app.db import Session
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from pipeline.configure_logging import configure_logging
import logging

configure_logging()
logger = logging.getLogger("api_ashby")

board_tokens = ["terminal", "unblocked"]


def add_job(job):
    """Create SQLAlchemy statement for save to database"""
    new_job = {
        "id": str(job["id"]),
        "title": job["title"],
        "employer_name": job["company_name"],
        "location": job["location"],
        "num_applications": None, #job["applications"],
        "min_salary": None, #job["minimumSalary"],
        "max_salary": None, #job["maximumSalary"],
        "date_posted": datetime.fromisoformat(job["first_published"]).date(),
        "date_expires": datetime.fromisoformat(job["application_deadline"]).date() if job["application_deadline"] else None,
        "job_description": job["content"],
        "job_url": job["jobUrl"],
    }

    stmt = insert(GreenhouseRaw).values(new_job) # change
    stmt = stmt.on_conflict_do_nothing(
            index_elements=[GreenhouseRaw.id]  # change
        )

    return stmt





def get_ashby_data(slug):
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"

    response = requests.get(url)
    print("type of response = ", type(response))
    json_data = response.json()
    print("type of json data = ", type(json_data))
    print("json data keys", json_data.keys())
    print(json.dumps(json_data["jobs"][0], indent=2))
    logger.info(f"Retrieved {len(json_data['jobs'])}")

    logger.info(f"Committing {slug} jobs to database")
    with Session() as db_session:
        for job in json_data["jobs"]:
            if "london" in job["location"].lower():
                stmt = add_job(job)
                db_session.execute(stmt)
                db_session.commit()

for token in board_tokens:
    get_ashby_data(token)



logger.info("Ingestion complete from Ashby api")
