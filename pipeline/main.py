import yaml
from . import api_calls
from . import filters
from app.db import Session
from sqlalchemy.dialects.postgresql import insert
# from datetime import datetime # , timezone
from app.models import CandidateJob    # DOWNSTREAM
from pipeline.configure_logging import configure_logging
import logging

configure_logging()
logger = logging.getLogger("pipeline.main")


def save_candidate_jobs(candidate_jobs: list[dict]) -> bool:
    logger.info("attempting to save to db")
    try:
        db_session = Session()

        values = candidate_jobs

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
    logger.info(f"Attempting to get data from {company['name']}")
    jobs = api_calls.get_company_data(company)
    
    logger.info(f"Number of jobs from {company['name']} is {len(jobs)}")
    logger.info(f"In main loop, attempting to save {company["name"]} to DB.")

    # filters go here
    jobs_to_save = []
    for job in jobs:
        if filters.passes_filters(job):
            jobs_to_save.append(job)
    logger.info(f"Number of jobs that passed filtering: {len(jobs_to_save)}")
    if len(jobs_to_save) > 0:
        save_candidate_jobs(jobs)