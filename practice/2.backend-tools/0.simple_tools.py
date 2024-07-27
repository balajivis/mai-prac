from groq import Groq
import json
from dotenv import load_dotenv
load_dotenv()
import math 

client = Groq()
MODEL = 'llama3-groq-70b-8192-tool-use-preview' # no math here.

# LLM output

def calculate(expression):
    """Evaluate a mathematical expression"""
    print(expression)
    try:
        result = eval(expression, {"math": math})
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})

def run_conversation(user_prompt):
    messages = [
        {
            "role": "system",
            "content": (
                "You must use the tool if it is a math problem. You are a versatile calculator assistant capable of performing a wide range of mathematical operations. "
                "You can handle basic arithmetic, exponentiation, modulus, and other advanced mathematical functions. "
                "Use the calculate function to evaluate the given expressions and provide accurate results. "
                "Here are some examples of operations you can perform:\n"
                "- Addition: 5 + 3\n"
                "- Subtraction: 10 - 2\n"
                "- Multiplication: 4 * 7\n"
                "- Division: 20 / 4\n"
                "- Exponentiation: 2 ** 3\n"
                "- Modulus: 10 % 3\n"
                "- Complex expressions: (5 + 3) * 2 - 4 / 2\n"
                "- Trigonometric functions: math.sin(math.pi / 2)\n"
                "- Logarithmic functions: math.log(100, 10)\n"
                "- Square root: math.sqrt(16)\n"
                "Provide your mathematical expression for evaluation."
            )   },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Evaluate a mathematical expression",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "The mathematical expression to evaluate",
                        }
                    },
                    "required": ["expression"],
                },
            },
        }
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=4096
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    print(tool_calls)
    
    if tool_calls:
        for tool_call in tool_calls:
            function_arguments = json.loads(tool_call.function.arguments)
            function_response = calculate(function_arguments.get("expression"))
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_call.function.name,
                "content": function_response,
            })
        
        second_response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )
        return second_response.choices[0].message.content

    return response_message.content

while True:
    user_input = input("You: ")
    if user_input.lower() == "/bye":
        print("Session ended. Goodbye!")
        break

    print("Assistant: " + run_conversation(user_input))
