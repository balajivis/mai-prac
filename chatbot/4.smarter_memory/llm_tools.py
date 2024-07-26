import json
from dotenv import load_dotenv
from groq import Groq
from scheduler_tools import get_today, view_slots, parse_date, book_appointment, submit_complaint, cancel_appointment

load_dotenv()

client = Groq()
MODEL = 'llama3-groq-70b-8192-tool-use-preview'



def call_llm(user_prompt, memory):
    basic_prompt = """You are Mitra, an assistant for Modern AI Pro -- an edtech tool. You have to help people schedule sessions. 
                Be nice, polite, and friendly. Keep the responses around 2-3 sentences. 
                People can view available slots for 4 things: lab sessions, book office hour appointments, submit complaints, and cancel appointments.
                They might be able to say 'Are there available sessions for tomorrow?'
                """
    prompt = (
        f"Today is: {get_today()}\n"
        f"{basic_prompt}\n"
        "Here is the recent interaction with the user taken from the session memory:\n"
        f"{memory['session_memory']}\n"
        "This is the long term info about the user loaded from memory:\n"
        f"{memory['long_term_memory']}\n"
        "Combine this with the user's message:\n"
        )
     
    # print (prompt)
    
    messages = [
        {
            "role": "system",
            "content": prompt
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]


    tools = [
        {
            "type": "function",
            "function": {
                "name": "view_slots",
                "description": "View available slots for appointments on a specific date",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "The date to view available slots (YYYY-MM-DD, 'today', 'tomorrow')",
                        }
                    },
                    "required": ["date"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "book_office_hour",
                "description": "Book an office hour appointment on a specific date and time",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "The date to book the office hour appointment (YYYY-MM-DD, 'today', 'tomorrow')",
                        },
                        "time": {
                            "type": "string",
                            "description": "The time to book the office hour appointment (HH:MM)",
                        },
                        "name": {
                            "type": "string",
                            "description": "The name of the person booking the appointment",
                        },
                        "phone": {
                            "type": "string",
                            "description": "The phone number of the person booking the appointment",
                        }
                    },
                    "required": ["date", "time", "name", "phone"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "submit_complaint",
                "description": "Submit a complaint",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "complaint": {
                            "type": "string",
                            "description": "The complaint to submit",
                        },
                        "name": {
                            "type": "string",
                            "description": "The name of the person submitting the complaint",
                        }
                    },
                    "required": ["complaint", "name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "cancel_appointment",
                "description": "Cancel an existing appointment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the person who booked the appointment",
                        },
                        "phone": {
                            "type": "string",
                            "description": "The phone number of the person who booked the appointment",
                        }
                    },
                    "required": ["name", "phone"],
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
    print(response_message)
    
    tool_calls = response_message.tool_calls
    if tool_calls:
        available_functions = {
            "view_slots": view_slots,
            "book_office_hour": book_appointment,
            "submit_complaint": submit_complaint,
            "cancel_appointment": cancel_appointment,
        }
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            print(f"Tool call: {function_name}, Arguments: {function_args}")
            if function_name == "view_slots":
                date = parse_date(function_args.get("date"))
                function_response = function_to_call(
                    date=date
                )
            elif function_name == "book_office_hour":
                date = parse_date(function_args.get("date"))
                function_response = function_to_call(
                    date=date,
                    time=function_args.get("time"),
                    name=function_args.get("name"),
                    phone=function_args.get("phone")
                )
            elif function_name == "submit_complaint":
                function_response = function_to_call(
                    complaint=function_args.get("complaint"),
                    name=function_args.get("name")
                )
            elif function_name == "cancel_appointment":
                function_response = function_to_call(
                    name=function_args.get("name"),
                    phone=function_args.get("phone")
                )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        second_response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )
        return second_response.choices[0].message.content
    else:
        return response_message.content