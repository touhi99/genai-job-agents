#define tools
from ast import List
from langchain.agents import tool
from data_loader import load_cv, write_to_docx
from search import job_threads, get_job_ids
import asyncio
import os 
@tool
def job_pipeline(keywords: str, location_name:str, job_type:str=None, limit:int=10, companies:str=None, industries:str=None, remote:str=None) -> dict: # type: ignore
    """
    Search LinkedIn for job postings based on specified criteria. Returns detailed job listings.

    Parameters:
    keywords (str): Keywords describing the job role.
    location_name (str): Geographic location for the job search.
    job_type (str, optional): Specific type of job to search for.
    limit (int, optional): Maximum number of jobs to retrieve.
    companies (str, optional): Filter jobs by company names.
    industries (str, optional): Filter jobs by industry types.
    remote (str, optional): Specify if the jobs should be remote.

    Returns:
    dict: A dictionary containing job titles, company URLs, job locations, and detailed job descriptions.
    """
    job_ids = get_job_ids(keywords, location_name, job_type, limit, companies, industries, remote)
    print(job_ids)
    job_desc = asyncio.run(job_threads(job_ids))
    return job_desc # type: ignore

@tool
def extract_cv() -> str:
    """
    Extract and structure job-relevant information from an uploaded CV.

    Returns:
    str: The text of the CV formatted to highlight skills, experience, and qualifications relevant to job applications, omitting personal information.
    """
    text = load_cv("tmp/cv.pdf")
    return text


@tool
def generate_letter_for_specific_job(cv_details: str, job_details: str):
    """
    Generate a tailored cover letter using the provided CV and job details. This function constructs the letter as plain text.

    Here is the specific prompt for the LLM as part of a function docstring, with additional instructions for developers.

    It should be in a code block, marked as `<prompt>`
    ```<prompt>
    Based on the CV details provided in {cv_details} and the job requirements listed in {job_details}, write a personalized cover letter. Ensure the letter articulates how the applicant's skills and experiences align with the job requirements.
    ```

    This format ensures that the IDE displays the prompt correctly, aiding developers in understanding the expected output without markdown parsing issues. The rest of the docstring is for developer guidance.
    """
    return 

"""
@tool
def generate_letter_for_specific_job(query: str):
    Create a cover letter tailored to a job description based on an uploaded CV.

    Parameters:
    query (str): The combined information of CV and job to tailor the cover letter.

    Returns:
    tuple: A message indicating the cover letter is ready, along with the absolute path for downloading the DOCX file.
    file = write_to_docx(query)
    abs_path = os.path.abspath(file) # type: ignore
    print(abs_path)
    return "Here is the download link: ",  abs_path
"""

def get_tools():
    return [job_pipeline, extract_cv, generate_letter_for_specific_job]

@tool
def func_alternative_tool(msg: str, members):
    """Router tool route message among different members"""
    members = ["Analyzer", "Generator", "Searcher"]
    options = ["FINISH"] + members
    # Using openai function calling can make output parsing easier for us
    function_def = {
        "name": "route",
        "description": "Select the next role.",
        "parameters": {
            "title": "routeSchema",
            "type": "object",
            "properties": {
                "next": {
                    "title": "Next",
                    "anyOf": [
                        {"enum": options},
                    ],
                }
            },
            "required": ["next"],
        },
    }
    return function_def