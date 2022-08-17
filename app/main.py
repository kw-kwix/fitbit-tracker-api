from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.oauth import OAuth2Server
from pydantic import BaseModel
from fitbit import Fitbit

from app.routers import items

app = FastAPI()

app.include_router(items.router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
    server = OAuth2Server(fitbit_id.client_id, fitbit_id.client_secret)
    server.browser_authorize()
    return server.fitbit.client.session.token.items()


@app.post("/api/fitbit/user")
def get_heart_rate(fitbit_info: FitbitInfo):
    fitbit = Fitbit(fitbit_info.client_id,
                    fitbit_info.client_secret, fitbit_info.access_token, fitbit_info.refresh_token)
    return fitbit.intraday_time_series('activities/heart', "2022-08-14")
