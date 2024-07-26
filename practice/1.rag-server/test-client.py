import requests

query = "What does Mitra robot do?"

response = requests.post(
    "http://localhost:8000/customer-service/invoke",
    headers={
        'accept': 'application/json',
        'Content-Type': 'application/json'
    },
    json={
        'input': query,
        'config': {},
        'kwargs': {}
    }
)
print(response.json())