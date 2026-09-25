import os

from groq import Groq


class GroqQuotaError(RuntimeError):
    pass


class GroqService:

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing in .env"
            )

        self.client = Groq(api_key=api_key)

        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-20b"
        )

    # =========================================================
    # ERROR HANDLING
    # =========================================================

    @staticmethod
    def _is_quota_error(exc):

        text = str(exc).lower()

        return any(
            value in text
            for value in [
                "429",
                "rate limit",
                "rate_limit",
                "quota",
                "too many requests",
                "resource exhausted",
            ]
        )

    # =========================================================
    # GROQ STRICT JSON SCHEMA NORMALIZER
    # =========================================================

    @classmethod
    def _normalize_schema(cls, node):

        if isinstance(node, dict):

            result = {}

            for key, value in node.items():

                result[key] = cls._normalize_schema(value)

            # -------------------------------------------------
            # ANY OBJECT MUST BE CLOSED
            # -------------------------------------------------

            if (
                result.get("type") == "object"
                or "properties" in result
            ):

                result["additionalProperties"] = False

                properties = result.get(
                    "properties",
                    {}
                )

                if properties:

                    result["required"] = list(
                        properties.keys()
                    )

            # -------------------------------------------------
            # $defs contains reusable object definitions
            # -------------------------------------------------

            if "$defs" in result:

                normalized_defs = {}

                for name, definition in result["$defs"].items():

                    normalized_defs[name] = cls._normalize_schema(
                        definition
                    )

                result["$defs"] = normalized_defs

            return result

        elif isinstance(node, list):

            return [
                cls._normalize_schema(item)
                for item in node
            ]

        return node

    # =========================================================
    # VALIDATE SCHEMA BEFORE SENDING TO GROQ
    # =========================================================

    @classmethod
    def _validate_groq_schema(cls, schema):

        errors = []

        def walk(node, path="$"):

            if isinstance(node, dict):

                if node.get("type") == "object":

                    if node.get(
                        "additionalProperties"
                    ) is not False:

                        errors.append(
                            f"{path}: missing "
                            "additionalProperties=false"
                        )

                    properties = node.get(
                        "properties",
                        {}
                    )

                    required = set(
                        node.get(
                            "required",
                            []
                        )
                    )

                    for field in properties:

                        if field not in required:

                            errors.append(
                                f"{path}: field '{field}' "
                                "is not required"
                            )

                for key, value in node.items():

                    walk(
                        value,
                        f"{path}/{key}"
                    )

            elif isinstance(node, list):

                for index, item in enumerate(node):

                    walk(
                        item,
                        f"{path}/{index}"
                    )

        walk(schema)

        if errors:

            raise RuntimeError(
                "Groq schema validation failed:\n"
                + "\n".join(errors)
            )

    # =========================================================
    # REAL-TIME BROWSER SEARCH
    # =========================================================

    def browser_search(self, prompt: str):

        try:

            response = (
                self.client
                .chat
                .completions
                .create(

                    model=self.model,

                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a real-time technical "
                                "research agent. Search the web "
                                "for current information. "
                                "Prefer official documentation, "
                                "research papers, original "
                                "announcements and official "
                                "repositories. "
                                "Never invent sources."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],

                    tools=[
                        {
                            "type": "browser_search"
                        }
                    ],

                    tool_choice="required",

                    reasoning_effort="low",

                    max_completion_tokens=5000,
                )
            )

            return (
                response
                .choices[0]
                .message
                .content
                or ""
            )

        except Exception as exc:

            if self._is_quota_error(exc):

                raise GroqQuotaError(
                    "Groq quota/rate limit reached "
                    "during Browser Search."
                ) from exc

            raise

    # =========================================================
    # STRUCTURED OUTPUT
    # =========================================================

    def structured(self, prompt: str, schema):

        try:

            # Generate Pydantic JSON schema
            raw_schema = schema.model_json_schema()

            # Convert it to Groq-compatible strict schema
            strict_schema = self._normalize_schema(
                raw_schema
            )

            # Validate BEFORE API request
            self._validate_groq_schema(
                strict_schema
            )

            response = (
                self.client
                .chat
                .completions
                .create(

                    model=self.model,

                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert Agentic AI "
                                "researcher, AI engineer and "
                                "technical LinkedIn writer. "
                                "Return only JSON matching "
                                "the supplied schema."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],

                    response_format={
                        "type": "json_schema",

                        "json_schema": {

                            "name": "linkedin_generation",

                            "strict": True,

                            "schema": strict_schema,
                        },
                    },

                    reasoning_effort="low",

                    max_completion_tokens=8000,
                )
            )

            content = (
                response
                .choices[0]
                .message
                .content
            )

            if not content:

                raise RuntimeError(
                    "Groq returned an empty response."
                )

            return schema.model_validate_json(
                content
            )

        except Exception as exc:

            if self._is_quota_error(exc):

                raise GroqQuotaError(
                    "Groq quota/rate limit reached "
                    "during structured generation."
                ) from exc

            raise