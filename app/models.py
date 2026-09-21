from .db import Base
from sqlalchemy import Column, Integer, Numeric, Boolean, String, Text, Date, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime

# RAW class must all have the same structure.

class ReedRaw(Base):
    __tablename__ = "raw_reed"

    id = Column(String, primary_key=True)
    job_title = Column(String)
    employer_name = Column(String)
    location = Column(String)
    num_applications = Column(Integer)
    min_salary = Column(Numeric)
    max_salary = Column(Numeric)
    date_posted = Column(Date)
    date_expires = Column(Date)
    job_description = Column(Text)
    job_url = Column(String(2048))
    ingestion_ts = Column(DateTime(),
                          default=lambda: datetime.now())

class GreenhouseRaw(Base):
    __tablename__ = "raw_greenhouse"

    id = Column(String, primary_key=True)
    job_title = Column(String)
    employer_name = Column(String)
    location = Column(String)
    num_applications = Column(Integer)
    min_salary = Column(Numeric)
    max_salary = Column(Numeric)
    date_posted = Column(Date)
    date_expires = Column(Date)
    job_description = Column(Text)
    job_url = Column(String(2048))
    ingestion_ts = Column(DateTime(),
                          default=lambda: datetime.now())


class CandidateJob(Base):
    __tablename__ = "candidate_jobs"

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    job_title = Column(String)
    employer_name = Column(String)
    location = Column(String)
    job_description = Column(Text)
    num_applications = Column(Integer)
    min_salary = Column(Numeric)
    max_salary = Column(Numeric)
    date_posted = Column(Date)
    date_expires = Column(Date)
    job_url = Column(String(2048))
    ingestion_ts = Column(DateTime())

    __table_args__ = (
        UniqueConstraint("source", "source_id", name="uq_candidate_jobs_source_source_id"),
    )
