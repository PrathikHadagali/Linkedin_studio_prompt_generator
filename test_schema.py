from dotenv import load_dotenv

from app.services.groq_service import GroqService
from app.services.schemas import CompleteGeneration


load_dotenv()


print("=" * 60)
print("Testing Groq Structured Output Schema")
print("=" * 60)


raw_schema = CompleteGeneration.model_json_schema()

print("\nRaw Pydantic schema generated.")


strict_schema = GroqService._normalize_schema(
    raw_schema
)

print("Schema normalized for Groq.")


GroqService._validate_groq_schema(
    strict_schema
)

print("\nSUCCESS!")
print(
    "Schema is compatible with Groq strict Structured Outputs."
)


print("\nTop-level fields:")

for field in strict_schema.get(
    "properties",
    {}
):

    print(
        f"  ✓ {field}"
    )


print("\nDefinitions:")

for name in strict_schema.get(
    "$defs",
    {}
):

    definition = strict_schema["$defs"][name]

    print(
        f"  ✓ {name}: "
        f"additionalProperties="
        f"{definition.get('additionalProperties')}"
    )