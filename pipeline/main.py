import yaml
from . import api_calls

with open('companies.yaml') as f:
    companies = yaml.safe_load(f)

for company in companies['companies']:
    print(f"Attempting to get data from {company['name']}")
    jobs = api_calls.get_company_data(company)
    print("Got jobs list")
    num = len(jobs)
    print(f"Number of jobs from {company['name']} is {num}")
    print(jobs[0])