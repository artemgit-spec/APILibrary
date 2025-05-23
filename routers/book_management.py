"""2.	Управление книгами (Защищено JWT):
o	CRUD операции для книг (Создание, Чтение, Обновление, Удаление).
o	Поля книги:
	ID (автоматически генерируемый)
	Название (строка, обязательное)
	Автор (строка, обязательное)
	Год публикации (число, необязательное)
	ISBN (строка, должен быть уникальным, необязательное)
	Количество экземпляров (число, по умолчанию 1, не может быть меньше 0)
"""
# оформлено по PEP8
#импорты нужно разделять
from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated

from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import Session

from schemes import CreateBookSchemas, UpdateBookSchemas
from db.db_model import Librarian, BorrowedBooks, Book, ReaderUser
from db.session_db import local_session_db

router_book = APIRouter(prefix='/books-management', tags = ['Управление книгами'])

@router_book.post("/create-book")
async def create_book(
    db:Annotated[Session,Depends(local_session_db)],
    new_book: CreateBookSchemas
    ):
    
    db.execute(
        insert(Book).values(
            title = new_book.title,
            author = new_book.author,
            year_public = new_book.year_public,
            num_ins = new_book.num_ins
            )
    )
    db.commit()
    return {"status":status.HTTP_201_CREATED, "detail":"Книга создана"}
    

@router_book.get('/info-books')
async def info_books(
    db:Annotated[Session, Depends(local_session_db)]
):
    books = db.scalars(select(Book)).all()
    return books
    
     
@router_book.get('/info-book/{id}')
async def info(
    id: int, 
    db:Annotated[Session, Depends(local_session_db)]
):
    requested_book = db.scalar(select(Book).where(Book.id == id))
    if not requested_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Такой книги нет"
        )
    return requested_book
    
    
@router_book.patch('/update-book/{id}')
async def update_book(
    id: int, 
    up_book: UpdateBookSchemas, 
    db:Annotated[Session, Depends(local_session_db)]
):
    requested_book = db.scalar(select(Book).where(Book.id == id))
    
    if not requested_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Такой книги нет"
            )
    
    db.execute(
        update(Book)
        .where(Book.id == id)
        .values(
            title=up_book.title,
            author=up_book.author,
            year_public=up_book.year_public
        )
    )
    db.commit()
    return {'status':status.HTTP_200_OK, "detail":"Информация обновлена"}
    
    
@router_book.delete("/delete-books/{id}")
async def delete_book(
    id: int, 
    db:Annotated[Session, Depends(local_session_db)]
):
    requested_book = db.scalar(select(Book).where(Book.id == id))
    if not requested_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Такой книги нет"
        )
    
    db.execute(delete(Book).where(Book.id == id))
    db.commit()
    return {'status':status.HTTP_200_OK, "detail":"Книга удалена"}
    
    
