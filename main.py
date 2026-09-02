# from fastapi import FastAPI, Depends, Request
# import time
# from sqlalchemy import create_engine, Column, Integer, String
# from sqlalchemy.orm import sessionmaker, declarative_base, Session

# DATABASE_URL = "sqlite:///./todo.db"

# app = FastAPI()

# @app.middleware('http')
# async def my_middleware(request : Request, call_next):

#     print("Request Recieved")
#     response = await call_next(request)
#     return response

# @app.middleware('http')
# async def log_middleware(request : Request, call_next):

#     start_time = time.time()

#     response = await call_next(request)

#     process_time = time.time() - start_time

#     print(f"Path : {request.url.path} | Time : {process_time}")

#     return response  

from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
import time
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = "sqlite:///./todo.db"

app = FastAPI()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine
)

Base = declarative_base()

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    completed = Column(String)

Base.metadata.create_all(bind=engine)


def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# @app.get("/")
# def home(db : Session = Depends(get_db)):
#     return {
#         "message" : "DB connected Successfully"
#     }

class TodoCreate(BaseModel):
    id : int
    title: str
    completed : str


# CREATE Todo (POST)
@app.post("/create-todo")
def create_todo(data_todo : TodoCreate, db: Session = Depends(get_db)):

    # Create a Todo object
    new_todo = Todo(
        title=data_todo.title,
        completed="false"
    )

    # Add it to the database session
    db.add(new_todo)

    # Save it permanently to SQLite
    db.commit()

    # Get the generated ID
    db.refresh(new_todo)

    return {
        "message" : "Todo created successfully",
        "data" : new_todo
    }

@app.get("/get-all")
def get_todos(db : Session = Depends(get_db)):

    todos = db.query(Todo).all()

    return{
        "Total Todos ": len(todos),
        "data" : todos
    }

@app.get("/todos/{todo_id}")
def get_todo_by_id(todo_id = int, db : Session = Depends(get_db)):

    todo = db.query(Todo).filter(Todo.id == todo_id).first()

    return{
        "message": "Todo fetched successfully",
        "data" : todo
    }