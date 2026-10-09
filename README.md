# Jobseeker
## Early development (architecture evolving) ** REFACTOR IN PROGRESS **

A job discovery and filtering project that ingests jobs from multiple APIs, stores them in PostgreSQL, filters for relevance and displays results through a Flask web interface.

## Architecture diagram
```
jobseeker/
├── Dockerfile
├── README.md
├── app
│   ├── __init__.py
│   ├── db.py
│   ├── models.py
│   ├── routes.py
│   ├── static
│   │   └── styles.css
│   └── templates
│       └── index.html
├── app.py
├── create_db.py
├── dev_notes.txt
├── pipeline
│   ├── __init__.py
│   ├── api_greenhouse.py
│   ├── api_reed.py
│   ├── configure_logging.py
│   ├── description.py
│   └── process.py
└── requirements.txt
```
## Database setup

This app runs in Docker and uses the PostgreSQL instance on the host machine.

### On host machine in psql:
```
CREATE DATABASE jobs_db;
CREATE USER jobs_user WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE jobs_db TO jobs_user;
\c jobs_db
GRANT ALL ON SCHEMA public TO jobs_user;
```
## TO RUN (Windows/WSL):

Start Docker desktop

From root directory: code .
Reopen in devcontainer
```
From terminal inside dev container:
(Initial setup only): python3 create_db.py (Creates necessary tables in jobs_db database)
RUN PIPELINE WITH: python3 -m pipeline.main
**Filters not yet refactored, so too many jobs will be displayed.**
RUN FLASK APP WITH: flask run
```
# Project Roadmap

## Current Status
- Reed API ingestion complete
- Greenhouse API ingestion implemented (raw storage)
- Candidate filtering pipeline operational
- Flask UI functional and serving filtered roles
- Postgres schema established

## Next Steps
### UI Improvements
- Display count of jobs on webpage
- Add "reject" and "applied" actions for job tracking

### Pipeline Enhancements
- Integrate Greenhouse processing into main pipeline
- Add Lever and additional APIs
- Improve filtering using job descriptions:
  - experience level detection
  - tech stack matching
  - red flag detection

### Data Engineering Features
- Normalisation across APIs
- Deduplication (cosine similarity or alternative)
- Scoring / ranking system
- RAG-based matching using master CV
