from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.config import setting
from app.datasourse.db_users import Base, engine
from app.datasourse import models  # регистрация таблиц SQLAlchemy
from app.web.auth_web import router
from app.authorization.JWT_autho import JWT_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Только для учебного проекта; в реальном приложении — Alembic.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title='Хранилище промптов', lifespan=lifespan)
origins = [x.strip() for x in setting('CORS_ORIGINS', 'http://localhost:5500,http://127.0.0.1:5500,http://localhost:63342,http://127.0.0.1:63342').split(',') if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                   allow_headers=['Authorization', 'Content-Type'])
app.include_router(router)
app.include_router(JWT_router)


@app.get('/', include_in_schema=False)
def home():
    return FileResponse(Path(__file__).resolve().parent / 'frontend' / 'index.html')
