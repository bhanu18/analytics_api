from typing import Union
from fastapi import FastAPI, Request
import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse

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
def requesttoken(request: Request, code: str = "", state: str = ""):

    if state != None:
        redirectTo = "http://127.0.0.1:8000"
        # Form the payload data
        payload = {"grant_type": "authorization_code", "code": code, "redirect": redirectTo}
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
    else:
        return RedirectResponse('/')


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
    else:
        return {"status": False}


@app.get("/login")
def login_spotify():
    scope = "user-read-private user-read-email"
    redirect_uri = "http://127.0.0.1:8000"
    state = "ahkjasfdkfureertfknf"

    return RedirectResponse(
        "https://accounts.spotify.com/authorize?"
        + "response_type="
        + "code"
        + "&client_id="
        + client_id
        + "&scope="
        + scope
        + "&redirect_uri="
        + redirect_uri
        + "&state="
        + state
    )
