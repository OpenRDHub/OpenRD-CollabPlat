from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.security import hash_password


async def generate_platform_id(db: AsyncSession) -> str:
    result = await db.execute(text("SELECT nextval('platform_id_seq')"))
    seq_val = result.scalar_one()
    return f"ORD{seq_val:06d}"


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username, User.is_deleted == 0)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_phone(db: AsyncSession, phone: str) -> User | None:
    stmt = select(User).where(User.phone == phone, User.is_deleted == 0)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    stmt = select(User).where(User.id == user_id, User.is_deleted == 0)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession, *, username: str, phone: str, password: str
) -> User:
    platform_id = await generate_platform_id(db)
    user = User(
        platform_id=platform_id,
        username=username,
        phone=phone,
        password_hash=hash_password(password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
