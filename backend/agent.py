from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
import random

SYSTEM_PROMPT = """You are an expert bank statement analyzer.
You have access to one tool:

- get_bank_rate: use this to get current bank FX rate

If a user asks you to give an estimate currency conversion for X transactions, use the tool.
"""

@tool
def get_bank_rate(fx: str) -> int:
    """Get current bank rate"""
    return round(random.uniform(0, 1), 3)


model = init_chat_model(
    "gpt-4o-mini",
    temperature=0.5,
    timeout=10,
    max_tokens=1000
)

agent = create_agent(
    model=model,
    tools=[get_bank_rate],
    system_prompt=SYSTEM_PROMPT
)
