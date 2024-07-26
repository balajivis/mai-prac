from conversation_memory import summarize_memory, update_memory

user_id = "Balaji19"
update_memory(user_id,"I want to cancel my appointment")
print(summarize_memory(user_id))
update_memory(user_id,"My name is Balaji")
print(summarize_memory(user_id))