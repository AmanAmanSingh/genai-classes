from dotenv import load_dotenv
from openai import OpenAI
import requests
import json
import os


load_dotenv()

client = OpenAI()


def run_command(cmd: str):
    result = os.system(cmd)
    return result


def read_file(path: str):
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(path: str, content: str):
    try:
        with open(path, "w") as f:
            f.write(content)
        return f"Successfully updated {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."

    return "Something went wrong"


# ---------- REGISTER TOOLS ----------
available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
    "read_file": read_file,
    "write_file": write_file,
}

SYSTEM_PROMPT = f"""
    You are an helpfull AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.

    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.

    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    - "get_weather": Takes a city name as an input and returns the current weather for the city
    - "run_command" : Takes linux command as a string and executes the command and returns the output after executing it.
    - "read_file": file path → file contents
    - "write_file": file path + content → update file
 
    Example 1:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}

    Example 2:
    Output: {{ "step": "plan", "content": "The user wants a new Python file that prints Hello Aman" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call write_file with path hello.py and content" }}
    Output: {{ "step": "action", "function": "write_file", "input":  "path": "hello.py", "content": "print('Hello Aman')"  }}
    Output: {{ "step": "observe", "output": "Successfully updated hello.py" }}


"""


messages = [{"role": "system", "content": SYSTEM_PROMPT}]

while True:
    query = input("> ")

    messages.append({"role": "user", "content": query})

    while True:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            response_format={"type": "json_object"},
        )

        messages.append(
            {"role": "assistant", "content": response.choices[0].message.content}
        )
        parsed_response = json.loads(response.choices[0].message.content)

        if parsed_response.get("step") == "plan":
            print(f"🧠: {parsed_response.get("content")}")
            continue

        if parsed_response.get("step") == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            print(f"🛠️: Calling Tool:{tool_name} with input {tool_input}")

            # special case: write_file needs path + content
            if tool_name == "write_file" and isinstance(tool_input, dict):
                output = available_tools[tool_name](
                    tool_input.get("path"),
                    tool_input.get("content"),
                )
            else:
                output = available_tools[tool_name](tool_input)

            messages.append(
                {
                    "role": "user",
                    "content": json.dumps({"step": "observe", "output": output}),
                }
            )
            continue

        # Handle tools with multiple inputs (like write_file)
        if parsed_response.get("step") == "write_file":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            output = available_tools[tool_name](tool_input)
            messages.append(
                {
                    "role": "user",
                    "content": json.dumps({"step": "write_file", "output": output}),
                }
            )
            continue

        if parsed_response.get("step") == "output":
            print(f"🤖: {parsed_response.get("content")}")
            break

        # print(messages)
