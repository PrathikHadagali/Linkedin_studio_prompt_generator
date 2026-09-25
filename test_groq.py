from dotenv import load_dotenv
from app.services.groq_service import GroqService

load_dotenv()

groq = GroqService()
print("Testing Groq model:", groq.model)

response = groq.client.chat.completions.create(
    model=groq.model,
    messages=[{
        "role": "user",
        "content": "Explain the difference between an LLM and an AI agent in exactly three concise sentences."
    }],
    max_completion_tokens=300,
    reasoning_effort="low",
)

print(response.choices[0].message.content)
