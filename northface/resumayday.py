"""
Adapted from:
https://medium.com/@msalmon00/web-scraping-job-postings-from-indeed-96bd588dcb4b
"""

import logging
import requests
import urllib.parse

from bs4 import BeautifulSoup
from tqdm import tqdm

from northface import keyme


def get_titles(soup):
    """
    Scrape titles from the soup.
    """
    jobs = []
    for div in soup.find_all(name="div", attrs={"class": "row"}):
        for a in div.find_all(name="a", attrs={"data-tn-element": "jobTitle"}):
            jobs.append(a["title"])
    return jobs


def get_links(soup):
    """
    Scrape job links from the soup.
    """
    links = []
    for div in soup.find_all(name="div", attrs={"class": "row"}):
        for a in div.find_all(name="a", attrs={"data-tn-element": "jobTitle"}):
            links.append(f"https://indeed.com{a['href']}")
    return links


def get_companies(soup):
    """
    Scrape company names from the soup.
    """
    companies = []
    for div in soup.find_all(name="div", attrs={"class": "row"}):
        company = div.find_all(name="span", attrs={"class": "company"})
        if len(company) > 0:
            for b in company:
                companies.append(b.text.strip())
        else:
            sec_try = div.find_all(
                name="span", attrs={"class": "result-link-source"}
            )
            for span in sec_try:
                companies.append(span.text.strip())
    return companies


def get_locations(soup):
    """
    Scrape locations from the soup.
    """
    locations = []
    spans = soup.findAll(
        "div", attrs={"class": "location accessible-contrast-color-location"}
    )
    for span in spans:
        locations.append(span.text)

    return locations


def get_summaries(soup):
    """
    Scrape short summaries from the soup.
    """
    summaries = []
    divs = soup.findAll("div", attrs={"class": "summary"})
    for div in divs:
        summaries.append(div.text.strip())
    return summaries


def get_long_summary_w_keywords(soup, num_keywords=10):
    """
    Get the long summary from a job's details page.
    """
    summaries = []

    for div in soup.find_all(
        name="div", attrs={"class": "jobsearch-jobDescriptionText"}
    ):
        for p in div.find_all(name="p"):
            summaries.append(p.text)
        for li in div.find_all(name="li"):
            summaries.append(li.text)
        for d in div.find_all(name="div"):
            summaries.append(d.text)

    text = "\n".join(summaries)
    keywords = keyme.get_keywords(text, topn=num_keywords)
    return text, keywords


def build_long_summaries_w_keywords(jobs):
    """
    For each job, make a request to fetch the longer job summary and extract
    its keywords.

    :param jobs list: An otherwise full-formed jobs JSON.
    """
    jobs_w_summaries = []

    logging.info("Extracting job descriptions and keywords...")
    for job in tqdm(jobs):
        link = job["link"]
        jobpage = requests.get(link)
        soup = BeautifulSoup(jobpage.text, "html.parser")
        summary, keywords = get_long_summary_w_keywords(soup)
        job["long_summary"] = summary
        job["keywords"] = keywords
        jobs_w_summaries.append(job)

    return jobs_w_summaries


def fetch_jobs(job_title, location, num_keywords=10):
    """
    Create nicely formatted job dictionaries from soup.
    """
    logging.warning(
        "This endoint is changing soon!. Results will soon return jobs and "
        "keywords in one call."
    )
    encoded_job = urllib.parse.quote(job_title)
    encoded_location = urllib.parse.quote(location)
    url = f"https://www.indeed.com/jobs?q={encoded_job}&l={encoded_location}"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    titles = get_titles(soup)
    companies = get_companies(soup)
    summaries = get_summaries(soup)
    links = get_links(soup)

    if not len(titles) == len(companies) == len(summaries) == len(links):
        raise ValueError("Inconsistent posting results!")

    jobs = []

    for i, title in enumerate(titles):
        job = {}
        job["id"] = i
        job["title"] = title
        job["company"] = companies[i]
        job["summary"] = summaries[i]
        job["link"] = links[i]
        jobs.append(job)

    new_jobs = build_long_summaries_w_keywords(jobs)

    return new_jobs


def fetch_keywords(job_title, location, num_keywords=10):
    """
    Fetch the keywords from a job report.
    """
    jobs = fetch_jobs(job_title, location, num_keywords=1)
    summaries = []

    for job in jobs:
        summaries.append(job["long_summary"])

    appended_summary = "\n".join(summaries)
    keywords = keyme.get_keywords(appended_summary, topn=num_keywords)
    return keywords


def fetch_jobs_w_keywords(job_title, location, num_keywords=10):
    """
    Fetch jobs and keywords in one swoop.
    """
    encoded_job = urllib.parse.quote(job_title)
    encoded_location = urllib.parse.quote(location)
    url = f"https://www.indeed.com/jobs?q={encoded_job}&l={encoded_location}"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    titles = get_titles(soup)
    companies = get_companies(soup)
    summaries = get_summaries(soup)
    links = get_links(soup)

    if not len(titles) == len(companies) == len(summaries) == len(links):
        raise ValueError("Inconsistent posting results!")

    jobs = []

    for i, title in enumerate(titles):
        job = {}
        job["id"] = i
        job["title"] = title
        job["company"] = companies[i]
        job["summary"] = summaries[i]
        job["link"] = links[i]
        jobs.append(job)

    new_jobs = build_long_summaries_w_keywords(jobs)

    # Get keywords
    keyword_summaries = []

    for job in jobs:
        keyword_summaries.append(job["long_summary"])

    appended_summary = "\n".join(keyword_summaries)
    keywords = keyme.get_keywords(appended_summary, topn=num_keywords)

    return {"jobs": new_jobs, "keywords": keywords}
