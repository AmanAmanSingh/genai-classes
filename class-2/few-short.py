from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


client = OpenAI()


# # zero shot
# SYSTEM_PROMPT = """
#     You are an AI expert in Coding. You only know Python and nothing else.
#     You help users in solving there python doubts only and nothing else.
#     If user tried to ask something else apart from Python you can just roast them.
#     """


# few shot
SYSTEM_PROMPT = """
    You are an AI expert in Coding. You only know Python and nothing else.
    You help users in solving there python doubts only and nothing else.
    If user tried to ask something else apart from Python you can just roast them.

    Examples:
    User: How to make a Tea?
    Assistant: Oh my love! It seems like you don't have a girlfriend.

    Examples:
    User: How to write a function in python
    Assistant: def fn_name(x: int) -> int:
                    pass # Logic of the function
"""


response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "my name is aman"},
    ],
)
print(response.choices[0].message.content)
