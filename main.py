from ipaddress import ip_address
from contextlib import asynccontextmanager
from pathlib import Path

import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.routes import contacts, auth, users
from src.database.db import get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Підключення до Redis
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD
    )
    await FastAPILimiter.init(r)
    app.state.redis = r
    
    # Yield управління життєвим циклом
    yield

    # Закриття підключення до Redis
    await r.close()
    app.state.redis = None

# Ініціалізація FastAPI з контекстним менеджером lifespan
app = FastAPI(lifespan=lifespan)

# Додаємо middleware для CORS (як приклад)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path('.')
app.mount("/static", StaticFiles(directory=BASE_DIR/"src"/"static"))

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")

templates = Jinja2Templates(directory=BASE_DIR/"src"/"templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('index.html', context={"request": request, "our": "Here was me! Mew was here!"})

@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")