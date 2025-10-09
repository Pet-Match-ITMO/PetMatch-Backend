from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

class DBHelper:
    def __init__(self, db_url: str) -> None:
        self.engine = create_async_engine(db_url)
    
    def make_session(self):
        session_maker = async_sessionmaker(bind=self.engine)
        return session_maker()