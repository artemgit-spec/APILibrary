from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated

from datetime import datetime, timedelta

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import Session

from schemes import LibrarianSchemes
from db.db_model import Librarian
from db.session_db import local_session_db


router_lib = APIRouter(prefix="libraria", tags=["Регистрация и проверка библиотекаря"])
bcrypt = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2 = OAuth2PasswordBearer(tokenUrl="auth/token")

SECRET_KEY = "aaf3242fdbcv"
ALGORITHM = "HS256"


async def auth_lib(
    db:Annotated[Session, Depends(local_session_db)],
    login: str,
    entered_pass: str
):
    user = db.scalar(select(Librarian).where(Librarian.name==login))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Нет такого пользователя'
    )
    if not bcrypt.verify(entered_pass, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильные авторизационные данные",
            headers={'WWW-Authenticate':"Bearer"}
    )
    return user

async def create_token(
    username:str, 
    password: str, 
    expires_delta: timedelta
):
    expires = datetime.now() + expires_delta
    encode = {'sub':username, 'pass':password, 'exp':expires}
    return jwt.decode(encode, SECRET_KEY, algorithms=ALGORITHM)


async def current_user(token:Annotated[str, Depends(oauth2)]): #эта функция внедряется в каждую конечную точку приложения
    try:
        check_user = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        name = check_user.get('sub')
        password = check_user.get('pass')
        expire = check_user.get('exp')
        if name is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неправильные авторизационные данные"
            )
            
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удаётся получить токен доступа"
            )
            
        if datetime.now() > datetime.fromtimestamp(expire):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Истек срок действия токена"
            )
            
        return {'name':name, "password":password}
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неправильные авторизационные данные'
        )
    
    
@router_lib.post('/create-user')
async def create_user(
    db: Annotated[Session, Depends(local_session_db)],
    md_user: LibrarianSchemes 
):
    db.execute(
        insert(Librarian)
        .values(
            name=md_user.name,
            email=md_user.email,
            password=bcrypt.hash(md_user.password)
        )
    )
    db.commit()
    return {'status_code':status.HTTP_201_CREATED, "detail":"Пользователь создан"}


@router_lib('/token')
async def login(
    db:Annotated[Session, Depends(local_session_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = auth_lib(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось подтвердить пользователя"
        )

    token = create_token(user.name, user.password, expires_delta=timedelta(minutes=30))   
    return {'access_token':token, 'token_type':'bearer'}


@router_lib.get("/")
async def read_user(user:Annotated[Librarian, Depends(oauth2)]):
    return user
    

   
    