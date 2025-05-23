"""4.	Выдача и возврат книг (Защищено JWT):
o	Эндпоинт для выдачи книги читателю:
	Принимает book_id и reader_id.
	Бизнес-логика 1: Книгу можно выдать, только если есть доступные экземпляры (количество экземпляров > 0). При выдаче количество экземпляров уменьшается на 1.
	Фиксируется факт выдачи (например, в отдельной таблице BorrowedBooks с полями id, book_id, reader_id, borrow_date, return_date (изначально NULL)).
	Бизнес-логика 2: Один читатель не может взять более 3-х книг одновременно.
o	Эндпоинт для возврата книги читателем:
	Принимает book_id и reader_id (или borrow_id если используете отдельную таблицу).
	При возврате количество экземпляров соответствующей книги увеличивается на 1.
	В записи о выдаче проставляется return_date.
	Бизнес-логика 3: Нельзя вернуть книгу, которая не была выдана этому читателю или уже возвращена.
"""
""" Библиотекарь:
 Только библиотекари имеют аккаунты с паролями и проходят аутентификацию в системе.
📌 Читатели (ReaderUser) — это просто объекты данных, которых создаёт, редактирует и удаляет библиотекарь. У читателей нет логина, пароля и доступа к системе.
Имеет логин (имя/email) и пароль.

Может войти в систему (получить токен).

Может выполнять действия:

создать, изменить или удалить читателя;

выдать книгу читателю;

посмотреть, кто что взял;

вернуть книгу и т. д.

библиотекарь выбирает, кому выдать книгу.

🚫 Читатель:
Не имеет учётной записи, логина или пароля.

Не может зайти в систему.

Его данные заносятся вручную библиотекарем.

Например: "Иван Иванов", email="ivan@mail.ru", num_books=2 — просто запись в базе."""


from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated

from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import Session

from schemes import OutputBooksSchemas, ReturnBooksSchemas
from db.db_model import BorrowedBooks, Book, ReaderUser
from db.session_db import local_session_db

router_del_ret = APIRouter(prefix='/books', tags = ["Выдача книг"])

@router_del_ret.post("/book_distribution")
async def distribution(
    output: OutputBooksSchemas,
    db: Annotated[Session, Depends(local_session_db)]  
):
    book = db.scalar(select(Book).where(Book.id == output.book_id))
    user = db.scalar(select(ReaderUser).where(ReaderUser.id == output.reader_id))
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Такой книги нет'
        )
        
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет такого пользователя'
        )    
    
    if book.num_ins == 0:
        return {'message':'На складе осталось 0 экземпляров книг'}
    else: 
        book.num_ins -= 1
    
    if user.num_book == 3:
        return {'message':"У этого пользоватея уже ТРИ книги"}
    else:
        user.num_book += 1
    
    output_book = BorrowedBooks(
        book_id = output.book_id,
        reader_id = output.reader_id,
        borrow_date = output.borrow_date
    )
    
    db.add(output_book)
    db.commit()
    return {'status_code':status.HTTP_200_OK, "detail":"Книга выдана"}

@router_del_ret.patch("/book_distribution")
async def refund(
    ret_book: ReturnBooksSchemas,
    db:Annotated[Session, Depends(local_session_db)]
):
    book = db.scalar(select(Book).where(Book.id==ret_book.book_id))
    user = db.scalar(select(ReaderUser).where(ReaderUser.id==ret_book.reader_id))
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Такой книги нет'
        )
        
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет такого пользователя'
        )  
         
    return_book = db.scalar(
        select(BorrowedBooks)
        .where(
            (BorrowedBooks.book_id==ret_book.book_id) &
            (BorrowedBooks.reader_id==ret_book.reader_id)
        )
    )
    
    if not return_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет записи о выдачи книги'
        )
    
    book.num_ins += 1 
    user.num_book -= 1
    return_book.return_date = ret_book.return_date
    
    db.commit()
    
    return {'status_code':status.HTTP_200_OK, "detail":"Книга возвращена"}