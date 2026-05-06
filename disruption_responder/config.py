"""Environment loading and the shared LLM client."""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# i use litellm at work so trying that key first, otherwise normal openai
_API_KEY = os.getenv("LITELLM_API_KEY") or os.getenv("OPENAI_API_KEY")
_API_BASE = os.getenv("LITELLM_API_BASE") or os.getenv("OPENAI_BASE_URL")
_MODEL = os.getenv("DR_MODEL", "gpt-5")


def make_llm(model: str | None = None, temperature: float = 0) -> ChatOpenAI:
    """Build a ChatOpenAI client from env. Override `model` per agent if needed."""
    return ChatOpenAI(
        model=model or _MODEL,
        temperature=temperature,
        api_key=_API_KEY,
        base_url=_API_BASE,
    )


# default singleton used by the agents
llm = make_llm()
