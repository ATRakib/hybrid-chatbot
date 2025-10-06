from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes import chat, train

app = FastAPI(title="Hybrid Search Chatbot")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(chat.router, prefix="/api")
app.include_router(train.router, prefix="/api")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/train")
async def train_page(request: Request):
    return templates.TemplateResponse("train.html", {"request": request})