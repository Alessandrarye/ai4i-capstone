from contextlib import asynccontextmanager
from fastapi import FastAPI

from .database import Base, engine
from .routes import readings


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Shop Floor Predictive Maintenance API", lifespan=lifespan)
app.include_router(readings.router)


@app.get("/health")
def health():
    return {"status": "ok"}
