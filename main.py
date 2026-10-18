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

from fastapi import FastAPI, Depends, Request, HTTPException
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

# GET (get-all todos)
@app.get("/get-all")
def get_todos(db : Session = Depends(get_db)):

    todos = db.query(Todo).all()

    return{
        "Total Todos ": len(todos),
        "data" : todos
    }

# GET (fetch single todo using todo_id)
@app.get("/todos/{todo_id}")
def get_todo_by_id(todo_id = int, db : Session = Depends(get_db)):

    todo = db.query(Todo).filter(Todo.id == todo_id).first()

    if not todo:

        raise HTTPException(status_code=404, detail="Todo not found")

    else: 

        return{
                "message": "Todo fetched successfully",
                "data" : todo
            }


@app.put("/todos/{todo_id}")
def update_todo(todo_id : int , title : str, completed : str, db : Session = Depends(get_db)):

    todo = db.query(Todo).filter(Todo.id == todo_id).first()

    if not todo:
    
            raise HTTPException(status_code=404, detail="Todo not found")
    
    # authomatcially send it into else case: 
    todo.title = title
    todo.completed = completed

    db.commit()

    db.refresh(todo)

    return{
        "message" : "Todo updated successfully",
        "data" : todo
    }

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id : int , db : Session = Depends(get_db)):

    todo = db.query(Todo).filter(Todo.id == todo_id).first()

    if not todo:
    
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)

    db.commit()

    # db.refresh(todo)

    return{
        "message" : "Todo deleted successfully",
    }


# Asynchronous Programming using (async - await)
import asyncio
import time
from fastapi import FastAPI

app = FastAPI()

# async def task():

#     await asyncio.sleep(3)
#     return "Done"

@app.get("/")
async def home():
    await asyncio.sleep(3)
    return {
        "message" : "Async API called"
    }

# ============================================================================================ 

# Authentication basics (JWT Token based Authentication)

# JWT token components : Header + Payload + Signature 
# Header :- It contains {"alg" : The algorithm that is used to create signature , "type": type of token}
# Payload :- The Payload contains information called claims or user details
# Signature :-  The Signature is used to verify that the JWT: 1)Was created by a trusted party.2) Has not been modified.

from fastapi import FastAPI, HTTPException, Depends, Header
from datetime import datetime, timedelta, timezone
from jose import jwt

app = FastAPI()

SECRET_KEY = "mysecretkey"

ALGORITHM = "HS256"

# Create a access token
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    to_encode.update({
        "exp": expire
    })

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

# Login API (Generate Token)
@app.post("/login")
def user_login(username : str, password : str):

    if username != "admin" or password != "12345":

        raise HTTPException(
            status_code=401,
            detail="Invalid username and password"
        )

    token = create_access_token({
        "sub" : username
    })

    return {
        "access_token": token
    }

# Verify Token
def verify_token(token: str = Header(None)):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return username

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

# Protected route
@app.get("/protected")
def protected_route(username: str = Depends(verify_token)):
    return {
        "message": "You have access to the protected route",
        "username": username
    }

# ===========================================================================================

# OAuth + JWT based Authentication
from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext

app = FastAPI()

# JWT Config
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password Hashing Setup
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# OAuth Setup
oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

# Dummy User DB
fake_user_db = {
    "admin" : {
        "username": "admin",
        "hashed_password" : pwd_context.hash("1234")
    }
}

# Hash Password
def hash_password(password : str):
    return pwd_context.hash(password)

# Verify Password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Create a access token
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    to_encode.update({
        "exp": expire
    })

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return token

# Login API (OAuth2 Form)
@app.post("/oauth-login")
def user_login(form_data : OAuth2PasswordRequestForm = Depends()):
    
    user = fake_user_db.get(form_data.username)

    if not user or not verify_password(form_data.password, user["hashed_password"]):

        raise HTTPException(
                    status_code=401,
                    detail="Invalid username and password"
        )
    access_token = create_access_token({"sub" : form_data.username})

    return {
        "access_token" : access_token,
        "token_type" : "bearer"
    }

# Verify Token
def verify_token(token: str = Depends(oauth2_schema)):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return username

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

# Protected route
@app.get("/protected")
def protected_route(username: str = Depends(verify_token)):
    return {
        "message": f"Hello {username}, you have the access to this protected route",
        "username": username
    }


# ===========================================================================================

# File Uploading using FastAPI

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
import os
import shutil

app = FastAPI()

UPLOAD_DIR = "uploads"

# STEP-1 : Ensures that the file is present or not
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# STEP-2 : Static file setup
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

# STEP-3 : Upload file API
@app.post("/upload")
def upload_file(file : UploadFile = File()):
    filename = file.filename

    file_path = os.path.join(UPLOAD_DIR, filename)

    if not filename:

        raise HTTPException(
            status_code=400,
            detail="File not found"
        )
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

        return{
            "message": "File uploaded successfully",
            "filename" : filename,
            "file_url" : f"http://127.0.0.1:8000/files/{filename}"
        }
    if not filename:
    
            raise HTTPException(
                status_code=400,
                detail="File not found"
            )
        

# STEP-3 : GET file url API
# @app.get("/files/{filename}")
# def get_file(filename : str):

#     file_path = os.path.join(UPLOAD_DIR, filename)



# ===========================================================================================

# CORS (Cross Origin Resource Sharing)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from config import setting

load_dotenv()

origin = setting.origin
SECRET_KEY = setting.SECRET_KEY

app.add_middleware(
    CORSMiddleware,
    allow_origins= origin, #Allowed origins
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def home():
    return {
        "message" : "CORS enabled API"
    }

# ===========================================================================================

# Third Party API Integration

from fastapi import FastAPI
import requests

app = FastAPI()

# GET all data
@app.get("/get-todos")
def get_posts():

    # GET the url
    url = "https://dummyjson.com/todos"

    # store the response from the url
    response = requests.get(url)

    # Parse it into json format and return
    return response.json()

# GET todos based on their id
@app.get("/todos/{todo_id}")
def get_posts(todo_id : int):

    # GET the url
    url = f"https://dummyjson.com/todos/{todo_id}"

    # store the response from the url
    response = requests.get(url)

    # Parse it into json format and return
    return response.json()


# ===========================================================================================

