from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# This lets frontend (running on a different port) talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/menu")
def get_menu():
    return [{"id": 1, "name": "Burger", "price": 9.99},{"id": 2, "name": "Fries", "price": 5.25}]
