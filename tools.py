#define tools
from langchain.agents import tool
from data_loader import load_cv
from search import job_threads, get_job_ids
import asyncio
from docx import Document

@tool
def job_pipeline(keywords: str, location_name:str, job_type:str=None, limit:int=10, companies:str=None, industries:str=None, remote:str=None) -> dict: # type: ignore
    """Given a query identify job role, location and other optional arguments: job type, search/hit limit, companies, industries, remote job 
    and returns a list of Linkedin job posting title, company url, job location and detailed job description
    """
    job_ids = get_job_ids(keywords, location_name, job_type, limit, companies, industries, remote)
    print(job_ids)
    job_desc = asyncio.run(job_threads(job_ids))
    return job_desc # type: ignore

@tool
def extract_cv() -> str:
    """Load the uploaded Resume/CV. From the CV text, extract relevant skill, experience, previous job responsibility, project experience etc.
    Returns the unstructured CV text in a structured format later to analyzer. Consider only job relevant skill, not any personal information"""
    text = load_cv("tmp/cv.pdf")
    return text

@tool
def generate_letter_for_specific_job(query: str) -> str:
    """Given the CV and highest relevant job, write a cover letter according to CV and matching with the job description. \
       Letter should contain contact info, proper addresser, some description of the career and motivation for this job.\
       Return the letter in a docx file format."""
    doc = Document()
    # Add a paragraph with the provided text
    doc.add_paragraph(query)
    # Save the document to the specified file
    filename = 'tmp/cover_letter.docx'
    doc.save(filename)
    print(f"Document saved")

    return filename  # type: ignore
