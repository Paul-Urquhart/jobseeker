import json
from app.db import Session
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime # , timezone
from app.models import ReedRaw, GreenhouseRaw    # SOURCES
from app.models import CandidateJob    # DOWNSTREAM
from pipeline.configure_logging import configure_logging
import logging

configure_logging()
logger = logging.getLogger("process")


# CONSTANTS

target_roles = [
    "analytics engineer",
    "data analyst",
    "data developer",
    "data engineer",
    "data infrastructure engineer",
    "data integration engineer",
    "data operations engineer",
    "data pipeline engineer",
    "data platform engineer",
    "data warehouse engineer",
    "early career",
    "etl developer",
    "etl engineer",
    "graduate",
    "new grad",
    "junior software engineer"
]

prohibited_words = [
    "c++",
    "centre",
    "consultant",
    "contract",
    "head",
    "ir35",
    "lead",
    "manager",
    "principal",
    "senior",
    "fabric"
]
prohibited_employers = [
    "IT Career Switch",
    "Newto Training",
    "ITOL Recruit"
]


# FUNCTIONS - GET DATA FROM RAW TABLES

def get_reed_data():
    db_session = Session()
    logger.info("connected to database")
    try:
        data = db_session.query(ReedRaw).order_by(ReedRaw.date_posted.desc()).all()
        logger.info("results retrieved")
    except Exception:
        logger.exception("exception occured in process.get_reed_data")
    finally:
        db_session.close()

    logger.info(f"Raw results: {len(data)}")

    return data

def get_greenhouse_data():
    db_session = Session()
    logger.info("connected to database")
    try:
        data = db_session.query(GreenhouseRaw).order_by(GreenhouseRaw.date_posted.desc()).all()
        logger.info("results retrieved")
    except Exception:
        logger.exception("exception occured in process.get_reed_data")
    finally:
        db_session.close()

    logger.info(f"Raw results: {len(data)}")

    return data

# FUNCTIONS - PROCESS AND FILTER DATA

def select_by_title(data):
    """Find jobs by desired title"""
    select_by_title = []

    for job in data:
        potential_candidate = False
        for target_role in target_roles:
            if target_role in job.job_title.lower():
                potential_candidate = True
        if potential_candidate == True:
            select_by_title.append(job)

    return select_by_title

def filter_jobs(select_by_title):
    """drop excluded terms from search"""
    filtered_jobs = []

    for job in select_by_title:
        prohibited = False
        for word in prohibited_words:
            if word in job.job_title.lower():
                prohibited = True
        if job.employer_name in prohibited_employers:
            prohibited = True
        if prohibited == False:
            filtered_jobs.append(job)

    logger.info(f"Filtered results: {len(filtered_jobs)} jobs")
    return filtered_jobs

# FUNCTIONS - FORMAT AND SAVE CANDIDATE JOBS

def reed_to_candidate_job(reed: ReedRaw) -> CandidateJob:
    return CandidateJob(
        source="reed",
        source_id=reed.id,
        job_title=reed.job_title,
        employer_name=reed.employer_name,
        location=reed.location,
        job_description=reed.job_description,
        num_applications=reed.num_applications,
        min_salary=reed.min_salary,
        max_salary=reed.max_salary,
        date_posted=reed.date_posted,
        date_expires=reed.date_expires,
        job_url=reed.job_url,
        ingestion_ts=reed.ingestion_ts
    )

def greenhouse_to_candidate_job(greenhouse: GreenhouseRaw) -> CandidateJob:
    return CandidateJob(
        source="greenhouse",
        source_id=greenhouse.id,
        job_title=greenhouse.job_title,
        employer_name=greenhouse.employer_name,
        location=greenhouse.location,
        job_description=greenhouse.job_description,
        num_applications=greenhouse.num_applications,
        min_salary=greenhouse.min_salary,
        max_salary=greenhouse.max_salary,
        date_posted=greenhouse.date_posted,
        date_expires=greenhouse.date_expires,
        job_url=greenhouse.job_url,
        ingestion_ts=greenhouse.ingestion_ts
    )

def save_candidate_jobs(candidate_jobs):
    logger.info("attempting to save to db")
    try:
        db_session = Session()

        values = [
            {
                "source": job.source,
                "source_id": job.source_id,
                "job_title": job.job_title,
                "employer_name": job.employer_name,
                "location": job.location,
                "job_description": job.job_description,
                "num_applications": job.num_applications,
                "min_salary": job.min_salary,
                "max_salary": job.max_salary,
                "date_posted": job.date_posted,
                "date_expires": job.date_expires,
                "job_url": job.job_url,
                "ingestion_ts": job.ingestion_ts
            }
            for job in candidate_jobs
        ]

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
    

# WORKFLOW:

# Process reed data
reed_data = get_reed_data()
selected_by_title = select_by_title(reed_data)
filtered_jobs = filter_jobs(selected_by_title)
logger.info("Converting from Reed to candidate job type")
candidate_jobs = [
    reed_to_candidate_job(reed)
    for reed in filtered_jobs
]
final_status = save_candidate_jobs(candidate_jobs)
logger.info(f"Processing complete for Reed: {final_status}")

# Process greenhouse data
greenhouse_data = get_greenhouse_data()
selected_by_title = select_by_title(greenhouse_data)
filtered_jobs = filter_jobs(selected_by_title)
logger.info("Converting from Greenhouse to candidate job type")
candidate_jobs = [
    greenhouse_to_candidate_job(greenhouse)
    for greenhouse in filtered_jobs
]
final_status = save_candidate_jobs(candidate_jobs)
logger.info(f"Processing complete for Greenhouse: {final_status}")