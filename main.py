from typing import Union, Optional
from fastapi import FastAPI, Request, Query
import httpx
import os
from os.path import join, dirname
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import uvicorn
import model.Item
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="some-random-string")

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

client_id = os.environ.get("clientid")
client_secret = os.environ.get("clientsecret")
redirect_uri = "http://127.0.0.1:8000/callback"

# HTTP timeout in seconds for external API calls
HTTP_TIMEOUT = 10.0


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
async def requesttoken(request: Request, code: str = "", state: str = ""):

    if state:
        # Form the payload data
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }

        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.post(
                "https://accounts.spotify.com/api/token",
                data=payload,
                auth=(client_id, client_secret),
            )

        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get("access_token")
            request.session["access_token"] = access_token
            return RedirectResponse("/me")
        else:
            return {"status": "Not sure"}
    else:
        return RedirectResponse("/")


@app.get("/login")
def login_spotify():
    scope = "user-read-private user-read-email playlist-read-private playlist-read-collaborative user-library-read"
    state = "ahkjasfdkfureertfknf"

    params = urlencode({
        "response_type": "code",
        "client_id": client_id,
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": state
    })

    return RedirectResponse(f"https://accounts.spotify.com/authorize?{params}")


@app.get("/artist")
async def getartist(request: Request):

    url = "https://api.spotify.com/v1/artists/2tIP7SsRs7vjIcLrU85W8J"

    bearer_token = request.session.get("access_token")

    header = {"Authorization": f"Bearer {bearer_token}"}

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        response = await client.get(url, headers=header)

    if response.status_code == 200:
        response_data = response.json()
        return {"status": True, "data": response_data}
    else:
        return {"status": False}


@app.get("/me")
async def getuserdata(request: Request):

    bearer_token = request.session.get("access_token")

    url = "https://api.spotify.com/v1/me"

    header = {"Authorization": f"Bearer {bearer_token}"}

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        response = await client.get(url, headers=header)

    if response.status_code == 200:
        response_data = response.json()
        return {"status": True, "data": response_data}
    else:
        return {"status": False}


@app.get("/mytracks")
async def gettopdata(
    request: Request,
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0)
):

    bearer_token = request.session.get("access_token")

    params = urlencode({
        "market": "TH",
        "limit": limit,
        "offset": offset
    })
    url = f"https://api.spotify.com/v1/me/tracks?{params}"

    header = {"Authorization": f"Bearer {bearer_token}"}

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        response = await client.get(url, headers=header)

    if response.status_code == 200:
        response_data = response.json()

        # Use dict comprehension for better performance
        tracks = {
            item['track']['name']: item['track']['href']
            for item in response_data['items']
        }

        return {
            "status": True,
            "data": tracks,
            "offset": response_data.get('offset', 0),
            "limit": response_data.get('limit', limit),
            "total": response_data.get('total', 0),
            "next": response_data.get('next')
        }
    else:
        return {"status": False}

@app.get("/myartist")
async def gettopartists(
    request: Request,
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    time_range: str = Query("medium_term", regex="^(short_term|medium_term|long_term)$")
):

    bearer_token = request.session.get("access_token")

    params = urlencode({
        "limit": limit,
        "offset": offset,
        "time_range": time_range
    })
    url = f"https://api.spotify.com/v1/me/top/artists?{params}"

    header = {"Authorization": f"Bearer {bearer_token}"}

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        response = await client.get(url, headers=header)

    if response.status_code == 200:
        response_data = response.json()

        # Use dict comprehension for better performance
        artists = {
            item['name']: item.get('external_urls', {}).get('spotify', '')
            for item in response_data['items']
        }

        return {
            "status": True,
            "data": artists,
            "offset": response_data.get('offset', 0),
            "limit": response_data.get('limit', limit),
            "total": response_data.get('total', 0),
            "next": response_data.get('next')
        }
    else:
        return {"status": False}


if __name__ == "__main__":
    uvicorn.run(app, debug=True)
