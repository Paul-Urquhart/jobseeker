import requests
from datetime import datetime

def get_ashby_data(company_name: str, slug: str) -> list[dict]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"

    response = requests.get(url)
    json_data = response.json()
    # logger.info(f"Retrieved {len(json_data['jobs'])}")

    jobs = []
    
    for job in json_data["jobs"]:
        if "london" in job["location"].lower():
            
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





FETCHERS = {
    "ashby": get_ashby_data
}


def get_company_data(company: dict) -> list[dict]:
    fetcher = FETCHERS.get(company['ats'])
    company_name = company['name']
    slug = company['slug']
    jobs = fetcher(company_name, slug)

    return jobs