import os
from dotenv import load_dotenv
from crewai.llm import LLM

# Load environment variables from .env file
load_dotenv()

# Get the Project ID and Region from the environment variables
gcp_project_id = os.getenv("GCP_PROJECT_ID")
gcp_region = os.getenv("GCP_REGION")

if not all([gcp_project_id, gcp_region]):
    raise ValueError("GCP_PROJECT_ID and GCP_REGION must be set in .env file")

# Set up Google Cloud project for Application Default Credentials
os.environ['GOOGLE_CLOUD_PROJECT'] = gcp_project_id

# Create the LLM object for CrewAI to use with Vertex AI Gemini
gemini_llm = LLM(
    model="vertex_ai/gemini-2.5-flash",  # Latest Gemini 2.5 model
    api_key="",  # Empty to use Application Default Credentials
    temperature=0.3
)

print(f"LLM object created successfully for Gemini 2.5 Flash model")
print(f"Using project: {gcp_project_id}, region: {gcp_region}")