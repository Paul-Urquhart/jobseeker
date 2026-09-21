import requests
import json
from app.models import GreenhouseRaw
from app.db import Session
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from pipeline.configure_logging import configure_logging
import logging

configure_logging()
logger = logging.getLogger("api_greenhouse")

board_tokens = ["stripe", "ohme"]


def add_job(job):
    """Create SQLAlchemy statement for save to database"""
    new_job = {
        "id": str(job["id"]),
        "job_title": job["title"],
        "employer_name": job["company_name"],
        "location": job["location"]["name"],
        "num_applications": None, #job["applications"],
        "min_salary": None, #job["minimumSalary"],
        "max_salary": None, #job["maximumSalary"],
        "date_posted": datetime.fromisoformat(job["first_published"]).date(),
        "date_expires": datetime.fromisoformat(job["application_deadline"]).date() if job["application_deadline"] else None,
        "job_description": job["content"],
        "job_url": job["absolute_url"],
    }

    stmt = insert(GreenhouseRaw).values(new_job)
    stmt = stmt.on_conflict_do_nothing(
            index_elements=[GreenhouseRaw.id]
        )

    return stmt





def get_greenhouse_data(board_token):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"

    response = requests.get(url)
    json_data = response.json()
    logger.info(f"Retrieved {len(json_data['jobs'])}")

    logger.info(f"Committing {board_token} jobs to database")
    with Session() as db_session:
        for job in json_data["jobs"]:
            if "london" in job["location"]["name"].lower():
                stmt = add_job(job)
                db_session.execute(stmt)
                db_session.commit()

for token in board_tokens:
    get_greenhouse_data(token)


# DEBUG:
# sample = json_data['jobs'][0]['first_published']
# logger.info(f"Type of first pub is {type(json_data['jobs'][0]['first_published'])}")
# published = datetime.fromisoformat(sample)

# print(published)
# print(published.strftime("%Y-%m-%d"))
# print(published.strftime("%d/%m/%Y"))




logger.info("Ingestion complete from Greenhouse api")





# job = raw['jobs'][0]
# with open("greenhouse_temp.json", "w") as file:
#     json.dump(json_data, file)


# import html
# from pathlib import Path

# # Input file
# input_file = Path("greenhouse_temp.json")

# # Output files
# pretty_json_file = Path("job_pretty.json")
# html_file = Path("job_description.html")

# # Read the JSON
# with input_file.open("r", encoding="utf-8") as f:
#     data = json.load(f)

# # Decode the HTML in the content field
# if "content" in data and data["content"]:
#     decoded_html = html.unescape(data["content"])
#     data["content"] = decoded_html

#     # Save the HTML separately
#     html_file.write_text(decoded_html, encoding="utf-8")
#     print(f"Saved HTML to {html_file}")

# # Save pretty-printed JSON
# with pretty_json_file.open("w", encoding="utf-8") as f:
#     json.dump(data, f, indent=2, ensure_ascii=False)

# print(f"Saved formatted JSON to {pretty_json_file}")