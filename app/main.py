from fastapi import FastAPI
from app.oauth import OAuth2Server
from pydantic import BaseModel
from fitbit import Fitbit
from fastapi.responses import RedirectResponse
from app.routers import items
from app.config import REDIRECT_URI

app = FastAPI()

app.include_router(items.router)


class FitbitID(BaseModel):
    client_id: str
    client_secret: str


class FitbitInfo(FitbitID):
    access_token: str
    refresh_token: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/api/fitbit/login")
def login_fitbit(fitbit_id: FitbitID):
    server = OAuth2Server(fitbit_id.client_id,
                          fitbit_id.client_secret, REDIRECT_URI)
    server.browser_authorize()
    return server.fitbit.client.session.token.items()


@app.get("/fitbit")
def fitbit(client_id: str, client_secret: str):
    fitbit = Fitbit(client_id, client_secret, redirect_uri=REDIRECT_URI)
    url, _ = fitbit.client.authorize_token_url()
    return RedirectResponse(url)


@app.get("/fitbit/auth")
def fitbit_auth(client_id: str, client_secret: str, code: str):
    fitbit = Fitbit(client_id, client_secret, redirect_uri=REDIRECT_URI)
    fitbit.client.fetch_access_token(code)
    return fitbit.client.session.token.items()


@app.post("/api/fitbit/heart")
def get_heart_rate(fitbit_info: FitbitInfo):
    fitbit = Fitbit(fitbit_info.client_id,
                    fitbit_info.client_secret, fitbit_info.access_token, fitbit_info.refresh_token)
    return fitbit.intraday_time_series('activities/heart', "today")


@app.post("/api/fitbit/distance")
def get_heart_rate(fitbit_info: FitbitInfo):
    fitbit = Fitbit(fitbit_info.client_id,
                    fitbit_info.client_secret, fitbit_info.access_token, fitbit_info.refresh_token)
    return fitbit.intraday_time_series('activities/distance', "today")
