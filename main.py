from typing import Union
from fastapi import FastAPI
import requests

app = FastAPI()

client_id = ""
client_secret = ""

bearer_token = ""

@app.post("/auth")
def requesttoken():
    # Form the payload data
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    # Set the headers
    headers = { 
        "Content-Type": "application/x-www-form-urlencoded"
    }
    res = requests.post(
        "https://accounts.spotify.com/api/token",
        data=payload,
        headers=headers
    )
    print(res)

@app.get('/artist')
def getartist():
    header = { 
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "Authorization": "Bearer " + bearer_token
    }
    res = requests.post('https://api.spotify.com/v1/artists/4Z8W4fKeB5YxbusRsdQVPb', data=payload, headers=header)

    print(res)