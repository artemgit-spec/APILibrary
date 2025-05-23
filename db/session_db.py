from db.db_model import local_session

async def local_session_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()