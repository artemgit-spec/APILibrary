from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class LibrarianSchemes(BaseModel):
    name: str
    email: EmailStr
    password: str
    
    
class ReaderUserSchemas(BaseModel):
    name: str
    email: EmailStr     
   
    
class CreateBookSchemas(BaseModel):
    title: str
    author: str
    year_public: int = Field(default = 0)
    num_ins:int = Field(default = 1, ge=0)
   
    
class UpdateBookSchemas(BaseModel):
    title: int
    author: str
    year_public: int
    
class OutputBooksSchemas:
    book_id: int
    reader_id: int
    borrow_date: datetime
    
    
class ReturnBooksSchemas:
    book_id: int
    reader_id: int
    return_date: datetime