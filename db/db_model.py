from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, DeclarativeBase, relationship
import uuid

engine = create_engine("sqlite:///library.db", echo = True)
local_session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
        pass
    
#таблица для библиотекарей    
class Librarian(Base):
    __tablename__ = "librarians"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
      
#таблица для читателя
class ReaderUser(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    num_book = Column(Integer, default=0)
    
    borrowed_books = relationship("BorrowedBooks", back_populates="user")
   
#таблица для книг
class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)# это значит что поле обязательно для заполнения
    author = Column(String, nullable=False)
    year_public = Column(Integer)
    isbn = Column(String, unique=True, default=lambda: str(uuid.uuid4())) # uuid для генерации случайных чисел
    num_ins = Column(Integer, default=1) #колличество экземпляров
    
    borrowed_books = relationship("BorrowedBooks", back_populates="book")
    
#таблица для фиксировании выдачи и возврата
class BorrowedBooks(Base): 
    __tablename__ = "borrowed_books"
    
    id = Column(Integer, primary_key = True)
    book_id = Column(Integer, ForeignKey('books.id'))
    reader_id = Column(Integer, ForeignKey('users.id'))
    borrow_date = Column(Date)
    return_date = Column(Date, default = None)
    
    book = relationship('Book', back_populates='borrowed_books')
    user = relationship('ReaderUser', back_populates='borrowed_books')
