import uvicorn

from fastapi import FastAPI

from routers.book_management import router_book
from routers.user_management import router_user


app = FastAPI(title = 'API для Библиотеки')

app.include_router(router_book)
app.include_router(router_user)

if __name__=="__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True)