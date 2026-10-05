import yaml

with open('filters.yaml') as f:
    filter_data = yaml.safe_load(f)

ALLOWED_LOCATIONS = filter_data["allowed_locations"]
RELEVANT_JOB_TITLES = filter_data["relevant_job_titles"]
EXCLUDED_TITLE_WORDS = filter_data["excluded_title_words"]


def location_is_allowed(job: dict) -> bool:
    return any(location.lower() in job["location"].lower() for location in ALLOWED_LOCATIONS)


def title_is_relevant(job: dict) -> bool:
    return (any(title.lower() in job["job_title"].lower() for title in RELEVANT_JOB_TITLES) 
            and not
    any(word.lower() in job["job_title"].lower() for word in EXCLUDED_TITLE_WORDS)
    )





def passes_filters(job: dict) -> bool:
    if location_is_allowed(job) and title_is_relevant(job):
        return True

