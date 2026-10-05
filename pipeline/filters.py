import yaml

def location_is_allowed(job: dict) -> bool:
    if "london" in job["location"].lower():
        return True
    return False






with open('filters.yaml') as f:
    filter_data = yaml.safe_load(f)

def passes_filters(job: dict) -> bool:
    if location_is_allowed(job):
        return True

