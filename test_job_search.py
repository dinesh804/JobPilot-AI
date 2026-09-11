from job_search import search_jobs


jobs = search_jobs(
    query="AI ML Engineer",
    location="Bangalore",
    country="in",
    results_per_page=5
)


print("\nJOBS FOUND")
print("=" * 60)

for job in jobs:
    print(f"\nTitle: {job.title}")
    print(f"Company: {job.company}")
    print(f"Location: {job.location}")
    print(f"Salary: {job.salary}")
    print(f"Source: {job.source}")
    print(f"URL: {job.job_url}")