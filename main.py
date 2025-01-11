from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from uvicorn import run

from app.auth.utils import get_access_token
from app.ideas.endpoints import idea_router
from app.repositories.user_repository import UserRepository, get_user_repository
from app.users.endpoints import user_router
from logging_app.logging_utils import get_logger, log_request, log_response, log_and_return_error_response


@asynccontextmanager
async def application_lifespan(app: FastAPI):
    print("starting")
    yield
    print("stopping")


app = FastAPI(lifespan=application_lifespan)
app.include_router(user_router)
app.include_router(idea_router)
logger = get_logger()
app.mount("/static", StaticFiles(directory="app/static"), "static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def get_base(req: Request):
    return templates.TemplateResponse(name='main_page.html', context={'request': req})

@app.get("/login")
async def login_form(req: Request):
    return templates.TemplateResponse(name='login_form.html', context={'request': req})

@app.get("/register")
async def reg_form(req: Request):
    return templates.TemplateResponse(name='register_form.html', context={'request': req})


@app.middleware("http")
async def log_requests_and_responses(request: Request, call_next):
    request_info = f"{request.method} {request.url}"
    log_request(logger, request_info)
    try:
        response = await call_next(request)
        log_response(logger, response.status_code, request_info)
        return response
    except Exception:
        return log_and_return_error_response(logger, request_info, exc_info=True)

@app.get("/profile")
async def get_profile(req: Request, session: UserRepository = Depends(get_user_repository), access_data: dict | bool = Depends(get_access_token)):
    return templates.TemplateResponse(name="profile.html", context={"request": req, "user": await session.get_user_by_id(access_data), "ideas": await session.count_ideas(access_data)})



# (Этот код должен быть скрыт в .env файле)
# На самом деле эти ключи лучше хранить в переменных окружения
# import os
# from dotenv import load_dotenv
# load_dotenv()

# aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
# aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")




if __name__ == "__main__":
    run("main:app", host="localhost", port=8000, reload=True)  # set some "debug=True" for development
