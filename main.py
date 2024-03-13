from typing import Union
from fastapi import FastAPI, Request
import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="some-random-string")

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

client_id = os.environ.get("clientid")
client_secret = os.environ.get("clientsecret")


@app.middleware("http")
async def some_middleware(request: Request, call_next):
    response = await call_next(request)
    session = request.cookies.get("session")
    if session:
        response.set_cookie(
            key="session", value=request.cookies.get("session"), httponly=True
        )
    return response


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/auth")
def requesttoken(request: Request):
    # Form the payload data
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    # Set the headers
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(
        "https://accounts.spotify.com/api/token", data=payload, headers=headers
    )
    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data.get("access_token")
        request.session["access_token"] = access_token
        return {"Access token:", access_token}


def apigetcall(request: Request, url, bearer_token):

    header = {"Authorization": "Bearer " + bearer_token}

    response = requests.get(url, headers=header)

    if response.status_code == 200:
        response_data = response.json()
        return response_data
    else:
        return False


@app.get("/artist")
def getartist(request: Request):

    url = "https://api.spotify.com/v1/artists/2tIP7SsRs7vjIcLrU85W8J"

    bearer_token = request.session.get("access_token")

    header = {"Authorization": "Bearer " + bearer_token}

    response = requests.get(url, headers=header)

    if response.status_code == 200:
        response_data = response.json()
        return {"status": True, "data": str(response_data)}
    else:
        return {"status": False}


@app.get("/me")
def getuserdata(request: Request):
    
    bearer_token = request.session.get("access_token")

    url = "https://api.spotify.com/v1/me"

    header = {"Authorization": "Bearer " + bearer_token}

    response = requests.get(url, headers=header)

    if response.status_code == 200:
        return {"status": True, "data": str(response)}
    elif response.status_code == 401 :
        response_data = response.json()
        return {"status": response_data['error']['message']}
    else:
        return {"status": False}