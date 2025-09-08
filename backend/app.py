from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import price, forecast, news

app = FastAPI(title="Stock Forecast & Sentiment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict to your frontend domain in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(price.router, prefix="/price", tags=["price"])
app.include_router(forecast.router, prefix="/forecast", tags=["forecast"])
app.include_router(news.router, prefix="/news", tags=["news"])
