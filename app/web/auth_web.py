import logging
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ollama import ResponseError
from app.authorization.JWT_autho import get_current_user, hash_password
from app.datasourse.db_users import get_db
from app.datasourse.models import User, Project
from app.domain.models.crt_usr import UserCreate, UserResponse, AiGenerateRequest, ProjectCreate, ProjectResponse
from app.domain.services.user_service import PromptService, UserService

router = APIRouter(tags=['Промпты и пользователи'])
logger = logging.getLogger(__name__)


@router.post('/users', response_model=UserResponse, status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(or_(User.username == user_in.username, User.email == user_in.email)).first():
        raise HTTPException(status_code=409, detail='Username or email already exists')
    try:
        return UserService().create_user(db, user_in.username, user_in.email, hash_password(user_in.password))
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail='Username or email already exists')


@router.get('/users', response_model=list[UserResponse])
def read_users(db: Session = Depends(get_db)):
    return UserService().read_users(db)


@router.get('/users/{user_id}', response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = UserService().read_users_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return user


@router.delete('/users/{user_id}', status_code=204)
def delete_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail='Can only delete your own account')
    UserService().delete_user(db, user_id)


@router.get('/protected/profile', response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post('/AI/generate')
def ai_generate(request: AiGenerateRequest):
    try:
        generated_prompt = PromptService().process_prompt(request.promt)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except httpx.TimeoutException as exc:
        logger.warning('Ollama timeout: %s', type(exc).__name__)
        raise HTTPException(status_code=504, detail='Ollama не ответила за 300 секунд') from exc
    except (httpx.ConnectError, ConnectionError, OSError, ResponseError) as exc:
        logger.exception('Ollama connection/model failure')
        raise HTTPException(status_code=503, detail='Не удаётся связаться с Ollama или загрузить модель') from exc
    return {'promt': generated_prompt}


@router.get('/projects', response_model=list[ProjectResponse])
def list_projects(q: str = Query(default='', max_length=200), skip: int = Query(0, ge=0),
                  limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    query = db.query(Project)
    if q.strip():
        query = query.filter(or_(Project.title.ilike(f'%{q.strip()}%'), Project.description.ilike(f'%{q.strip()}%')))
    return query.order_by(Project.created_at.desc(), Project.id.desc()).offset(skip).limit(limit).all()


@router.get('/projects/{project_id}', response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail='Prompt not found')
    return project


@router.post('/projects', response_model=ProjectResponse, status_code=201)
def create_project(body: ProjectCreate, current_user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    project = Project(**body.model_dump(), author_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.delete('/projects/{project_id}', status_code=204)
def delete_project(project_id: int, current_user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail='Prompt not found')
    if project.author_id != current_user.id:
        raise HTTPException(status_code=403, detail='Only author can delete prompt')
    db.delete(project)
    db.commit()
