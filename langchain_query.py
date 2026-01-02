"""Simple LangChain helper to ask GPT-4 a prompt.

Usage:
    export OPENAI_API_KEY="sk-..."
    from langchain_query import ask_gpt
    print(ask_gpt("Hello, how are you?"))
"""
import os
from typing import Optional

from dotenv import load_dotenv
from langchain_openai  import ChatOpenAI
from langchain_core.messages import HumanMessage


# Load environment variables from a local .env file (if present)
load_dotenv()


def ask_gpt(prompt: str, model: str = "gpt-5", temperature: float = 0.0, api_key: Optional[str] = None) -> str:
    """Ask a prompt to a GPT model via LangChain ChatOpenAI and return the assistant reply.

    Requires OPENAI_API_KEY to be set in the environment or passed via `api_key`.
    """
    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY environment variable is required")

    llm = ChatOpenAI(model=model, temperature=temperature, openai_api_key=key)
    resp = llm.invoke([HumanMessage(content=prompt)])
    return resp.content


if __name__ == "__main__":
    sample = "Write a short haiku about Python and AI."
    try:
        print(ask_gpt(sample))
    except Exception as e:
        print("Error calling GPT:", e)
