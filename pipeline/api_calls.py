import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import html
import os
from dotenv import load_dotenv
from pipeline.configure_logging import configure_logging
import logging

configure_logging()
logger = logging.getLogger("api_reed")
load_dotenv()
API_KEY_REED = os.environ.get('API_KEY_REED')

def get_ashby_data(company_name: str, slug: str) -> list[dict]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"

    response = requests.get(url)
    json_data = response.json()

    jobs = []
    
    for job in json_data["jobs"]:
            
        new_job = {
            "source": "Ashby",
            "source_id": str(job["id"]),
            "job_title": job["title"],
            "employer_name": company_name,
            "location": job["location"],
            "num_applications": None, #job["applications"],
            "min_salary": None, #job["minimumSalary"],
            "max_salary": None, #job["maximumSalary"],
            "date_posted": datetime.fromisoformat(job["publishedAt"]).date(),
            "date_expires": None,
            "job_description": job["descriptionHtml"],
            "job_url": job["jobUrl"],
        }
        jobs.append(new_job)

    return jobs



def get_greenhouse_data(company_name: str, slug: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"

    response = requests.get(url)
    json_data = response.json()
    
    jobs = []
    
    for job in json_data["jobs"]:

        # Decode the HTML in the content field
        if "content" in job and job["content"]:
            decoded_html = html.unescape(job["content"])
            job["content"] = decoded_html
        new_job = {
            "source": "Greenhouse",
            "source_id": str(job["id"]),
            "job_title": job["title"],
            "employer_name": company_name,
            "location": job["location"]["name"],
            "num_applications": None, #job["applications"],
            "min_salary": None, #job["minimumSalary"],
            "max_salary": None, #job["maximumSalary"],
            "date_posted": datetime.fromisoformat(job["first_published"]).date(),
            "date_expires": datetime.fromisoformat(job["application_deadline"]).date() if job["application_deadline"] else None,
            "job_description": job["content"],
            "job_url": job["absolute_url"],
        }
        jobs.append(new_job)

    return jobs


def get_reed_data(company_name=None, slug=None) -> list[dict]:

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
    

FETCHERS = {
    "ashby": get_ashby_data,
    "greenhouse": get_greenhouse_data,
    "reed": get_reed_data
}


def get_company_data(company: dict) -> list[dict]:
    fetcher = FETCHERS.get(company['ats'])
    company_name = company['name']
    slug = company['slug']
    jobs = fetcher(company_name, slug)

    return jobs