from fastapi import FastAPI
from controllers import (
    home_router,
    login_router,
    state_router,
    file_router,
)
from middlewares import common_middleware, exeption_handler
from utils.logging_config import configure_logging

configure_logging()

app = FastAPI(
    title="My API",
    description="This is my first API built with FastAPI",
    version="1.0.0"

)
app.include_router(home_router)
app.include_router(login_router)
app.include_router(state_router)
app.include_router(file_router)
app.add_middleware(exeption_handler)
app.add_middleware(common_middleware)
