import cohere

from app.core.config import COHERE_API_KEY, MODEL_NAME

_client = cohere.ClientV2(api_key=COHERE_API_KEY)


def call_llm(system_prompt: str, user_prompt: str) -> str:
    response = _client.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    if response and response.message and response.message.content:
        first = response.message.content[0]
        if hasattr(first, "text"):
            return first.text
        return str(first)

    return ""