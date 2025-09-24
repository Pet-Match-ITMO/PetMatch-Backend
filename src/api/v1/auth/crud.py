from loguru import logger
from passlib.context import CryptContext

from quart import abort

from sqlalchemy import select
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.user import User
from .scheme import RegisterRequest, LoginRequest
from .exceptions import DatabaseException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(session: AsyncSession, user_data: RegisterRequest):
    # Hash password with salt
    hashed_password = pwd_context.hash(user_data.password)
    try:
        user = User(
            email=user_data.email,
            username=user_data.username,
            password=hashed_password
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    except OperationalError as e:
        error_text = f"Database connection error: {e}"
        logger.error(error_text)
        raise DatabaseException(error_text)
    except IntegrityError as e:
        error_text = f"User cannot be created: {e}"
        logger.error(error_text)
        abort(400, description=error_text)


async def get_user_by_email(session: AsyncSession, email: str):
    try:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalars().first()
    except OperationalError as e:
        error_text = f"Database connection error: {e}"
        logger.error(error_text)
        raise DatabaseException(error_text)


async def authenticate_user(session: AsyncSession, credentials: LoginRequest):
    try:
        user = await get_user_by_email(session, credentials.email)
        if not user:
            return None
        
        # Verify password
        if not pwd_context.verify(credentials.password, user.password):
            return None
        
        return user

    except OperationalError as e:
        error_text = f"Database connection error: {e}"
        logger.error(error_text)
        raise DatabaseException(error_text)