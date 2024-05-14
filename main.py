from typing import Union
from fastapi import FastAPI, Request
import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
import base64
import uvicorn

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="some-random-string")

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

client_id = os.environ.get("clientid")
client_secret = os.environ.get("clientsecret")
redirect_uri = "http://127.0.0.1:8000/callback"


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


@app.get("/callback")
def requesttoken(request: Request, code: str = "", state: str = ""):

    if state != None:
        # Form the payload data
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }

        access_token = base64.urlsafe_b64encode(
            (client_id + ":" + client_secret).encode()
        )

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data=payload,
            auth=(client_id, client_secret),
        )

        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get("access_token")
            request.session["access_token"] = access_token
            return RedirectResponse("/me")
            # return {"status": True, "data": response_data}
        else:
            return {"status": "Not sure"}
    else:
        return RedirectResponse("/")


@app.get("/login")
def login_spotify():
    scope = "user-read-private user-read-email playlist-read-private playlist-read-collaborative user-library-read"
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
        response_data = response.json()
        return {"status": True, "data": response_data}
    else:
        return {"status": False}


@app.get("/mytracks")
def gettopdata(request: Request):

    tracks = {}
    bearer_token = request.session.get("access_token")

    url = "https://api.spotify.com/v1/me/tracks?market=TH"

    header = {"Authorization": "Bearer " + bearer_token}

    response = requests.get(url, headers=header)

    if response.status_code == 200:
        response_data = response.json()

        for i in response_data['items']:
            tracks[i['track']['name']] = i['track']['href'] 
        return {
            "status": True, 
            "data": tracks,
            "offset": response_data['offset']
        }
    else:
        return {"status": False}

@app.get("/myartist")
def gettopdata(request: Request):

    tracks = {}
    bearer_token = request.session.get("access_token")

    url = "https://api.spotify.com/v1/me/top/artists"

    header = {"Authorization": "Bearer " + bearer_token}

    response = requests.get(url, headers=header)

    if response.status_code == 200:
        response_data = response.json()

        for i in response_data['items']:
            tracks[i['name']] = i['url'] 
        return {
            "status": True, 
            "data": tracks,
            "offset": response_data['offset']
        }
    else:
        return {"status": False}


if __name__ == "__main__":
    uvicorn.run(app, debug=True)
