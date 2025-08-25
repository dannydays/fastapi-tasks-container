from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, List
import os

from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Task(BaseModel):
    nome: str
    descricao: str
    concluida: Optional[bool] = False

class TaskPost(BaseModel):
    nome: str
    descricao: str

class TaskResponse(BaseModel):
    id: int
    nome: str
    descricao: str
    concluida: bool

    class Config:
        from_attributes = True

class PaginatedTasksResponse(BaseModel):
    page: int
    limit: int
    total_items: int
    tasks: List[TaskResponse]

class TaskDB(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True, unique=True)
    descricao = Column(String, index=True)
    concluida = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_task_or_404(nome: str, db: Session = Depends(get_db)) -> TaskDB:
    """
    Busca uma tarefa no banco de dados pelo nome.
    Se não encontrar, levanta uma exceção HTTP 404.
    """
    task_db = db.query(TaskDB).filter(TaskDB.nome == nome).first()
    if not task_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Tarefa não encontrada!")
    return task_db

app = FastAPI()

username = os.getenv("USER")
password = os.getenv("PASS")

security = HTTPBasic()

# tasks: list[Task] = []

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username == username and credentials.password == password:
        return True
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Usuário ou senha inválidos",
                            headers={"WWW-Authenticate": "Basic"})

# Rota para ler todas as tarefas
@app.get("/tasks/", response_model=PaginatedTasksResponse, status_code=status.HTTP_200_OK)
def get_tasks(page: int = 1, limit:int = 3, sort_by: str = "id", db: Session = Depends(get_db), credentials: HTTPBasicCredentials = Depends(authenticate)):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Parâmetros inválidos: 'page' e 'limit' devem ser maiores que 0")
    
    allowed_sort_fields = ["id", "nome", "descricao", "concluida"]
    if sort_by not in allowed_sort_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Campo de ordenação inválido. Use um dos seguintes: {', '.join(allowed_sort_fields)}")
    
    offset = (page - 1) * limit

    tasks_query = db.query(TaskDB)

    sort_column = getattr(TaskDB, sort_by)
    tasks_query = tasks_query.order_by(sort_column)
    tasks = tasks_query.offset(offset).limit(limit).all()

    total_items = db.query(TaskDB).count()

    return {"page": page, "limit": limit, "total_items": total_items, "tasks": tasks}

# Rota para criar uma nova tarefa
@app.post("/tasks/", status_code=status.HTTP_201_CREATED)
def create_task(tarefa: TaskPost, db: Session = Depends(get_db), credentials: HTTPBasicCredentials = Depends(authenticate)):
    existing_task = db.query(TaskDB).filter(TaskDB.nome == tarefa.nome).first()
    if existing_task:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Tarefa já existe!")
    
    if not tarefa.nome or not tarefa.descricao:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Nome e descrição são obrigatórios!")
    
    task_db = TaskDB(nome=tarefa.nome, descricao=tarefa.descricao)
    db.add(task_db)
    db.commit()
    db.refresh(task_db)

    return {"message": f"Tarefa '{tarefa.nome}' criada com sucesso!"}

# Rota para marcar uma tarefa como concluída
@app.put("/tasks/check/{nome}", status_code=status.HTTP_200_OK)
def check_task(task_db: TaskDB = Depends(get_task_or_404), db: Session = Depends(get_db), credentials: HTTPBasicCredentials = Depends(authenticate)):
    task_db.concluida = True
    db.commit()
    db.refresh(task_db)
    
    return {"message": f"Tarefa '{task_db.nome}' marcada como concluída!"}

# Rota para deletar uma tarefa
@app.delete("/tasks/{nome}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_db: TaskDB = Depends(get_task_or_404), db: Session = Depends(get_db), credentials: HTTPBasicCredentials = Depends(authenticate)):
    db.delete(task_db)
    db.commit()
    
    return None