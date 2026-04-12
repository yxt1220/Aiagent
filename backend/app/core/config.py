import os
from dotenv import load_dotenv

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "command-a-03-2025")

PDF_DIR = os.getenv("PDF_DIR", "data/pdfs")
GUIDE_FILE = os.path.join(PDF_DIR, "guide.pdf")

RETRIEVAL_TOP_K = 4

USE_LLM_ROUTING_FALLBACK = False
USE_LLM_PEDAGOGICAL_REFINEMENT = False
USE_LLM_RESPONSE_GENERATION = True
USE_LLM_CONCEPT_EXTRACTION = True