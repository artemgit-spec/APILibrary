from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated

from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import Session

from schemes import ReaderUserSchemas
from db.db_model import ReaderUser, BorrowedBooks
from db.session_db import local_session_db

router_user = APIRouter(prefix='/users', tags = ["Управление пользователями"])



@router_user.get('/list-users')
async def list_users(
    db: Annotated[Session, 
    Depends(local_session_db)]
):
    users = db.scalars(select(ReaderUser)).all()
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="В вашей библиотеке нет читателей."
        )
    return users


@router_user.post('/create-user')
async def user_create(
    model_user: ReaderUserSchemas,
    db:Annotated[Session, Depends(local_session_db)]
):
    db.execute(
        insert(ReaderUser)
        .values(
            name=model_user.name,
            email=model_user.email
        ))
    db.commit()
    return {'status_code':status.HTTP_201_CREATED, "detail":"Пользователь создан"}
    
  
  
@router_user.patch('/update-user/{id}')
async def user_update(
    id: int, 
    up_user: ReaderUserSchemas,
    db: Annotated[Session, Depends(local_session_db)]
):
    user = db.scalar(select(ReaderUser).where(ReaderUser.id==id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="В вашей библиотеке нет читателей."
        )
        
    db.execute(
        update(ReaderUser)
        .where(ReaderUser.id==id)
        .values(
            name=up_user.name,
            email=up_user.email
        )
    )
    db.commit()
    return {'status_code':status.HTTP_200_OK, "detail":"Читатель изменен"}


@router_user.delete("/delete-user/{id}")
async def user_delete(
    id: int,
    db:Annotated[Session, Depends(local_session_db)]
):
    user = db.scalar(select(ReaderUser).where(ReaderUser.id==id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="В вашей библиотеке нет такого читателя."
        )
    
    db.execute(delete(ReaderUser).where(ReaderUser.id==id))
    db.commit()
    return {'status_code':status.HTTP_200_OK, "detail":"Читатель удален"}

@router_user.get("/list-books/{id}") #получаем список всех книг у пользователя.
async def list_book_user(
    id: int,
    db:Annotated[Session, Depends(local_session_db)]
):
    user = db.scalar(select(ReaderUser).where(ReaderUser.id == id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="В вашей библиотеке нет такого читателя."
        )
        
    borr_books = db.scalars(select(BorrowedBooks).where(BorrowedBooks.reader_id == id)).all()
    books_user = [ {
            "id": exemplar.book.id,
            "title": exemplar.book.title,
            "author": exemplar.book.author,
            "borrow_date": exemplar.borrow_date,
            "return_date": exemplar.return_date
        } 
        for exemplar in borr_books
    ]
    
    return {'list_books':books_user}
    