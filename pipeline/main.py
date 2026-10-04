import yaml
from . import api_calls
from app.db import Session
from sqlalchemy.dialects.postgresql import insert
# from datetime import datetime # , timezone
from app.models import CandidateJob    # DOWNSTREAM
from pipeline.configure_logging import configure_logging
import logging

configure_logging()
logger = logging.getLogger("pipeline.main")


def save_candidate_jobs(candidate_jobs):
    logger.info("attempting to save to db")
    try:
        db_session = Session()

        values = candidate_jobs
        # [
        #     {
        #         "source": job.source,
        #         "source_id": job.source_id,
        #         "job_title": job.job_title,
        #         "employer_name": job.employer_name,
        #         "location": job.location,
        #         "job_description": job.job_description,
        #         "num_applications": job.num_applications,
        #         "min_salary": job.min_salary,
        #         "max_salary": job.max_salary,
        #         "date_posted": job.date_posted,
        #         "date_expires": job.date_expires,
        #         "job_url": job.job_url,
        #         "ingestion_ts": job.ingestion_ts
        #     }
        #     for job in candidate_jobs
        # ]

        stmt = insert(CandidateJob).values(values)
        stmt = stmt.on_conflict_do_nothing(constraint="uq_candidate_jobs_source_source_id")
        result = db_session.execute(stmt)
        db_session.commit()

        inserted = result.rowcount
        skipped = len(values) - inserted
        logger.info(f"Inserted: {inserted}, skipped: {skipped}")
        return True
    except Exception:
        logger.exception("Failed to save candidate jobs")
        db_session.rollback()
        return False
    finally:
        db_session.close()

with open('companies.yaml') as f:
    companies = yaml.safe_load(f)

for company in companies['companies']:
    print(f"Attempting to get data from {company['name']}")
    jobs = api_calls.get_company_data(company)
    num = len(jobs)
    print(f"Number of jobs from {company['name']} is {num}")
    print(f"In main loop, attempting to save {company["name"]} to DB.")
    save_candidate_jobs(jobs)