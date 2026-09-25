from dotenv import load_dotenv
from app.services.groq_service import GroqService

load_dotenv()

groq = GroqService()
print("Testing Groq Browser Search:", groq.model)

result = groq.browser_search(
    "Research recent Agentic AI developments and provide a short summary with source URLs."
)

print(result)
