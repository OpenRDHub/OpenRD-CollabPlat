import json

from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.security import hash_password, verify_password


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


async def get_user_by_platform_id(db: AsyncSession, platform_id: str) -> User | None:
    stmt = select(User).where(User.platform_id == platform_id, User.is_deleted == 0)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession, *, username: str, phone: str, password: str, nickname: str | None = None
) -> User:
    platform_id = await generate_platform_id(db)
    user = User(
        platform_id=platform_id,
        username=username,
        phone=phone,
        password_hash=hash_password(password),
        nickname=nickname,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_profile(
    db: AsyncSession,
    user: User,
    *,
    nickname: str | None = None,
    avatar_url: str | None = None,
    province: str | None = None,
    occupation: str | None = None,
    bio: str | None = None,
    tags: list[str] | None = None,
) -> User:
    if nickname is not None:
        user.nickname = nickname
    if avatar_url is not None:
        user.avatar_url = avatar_url
    if province is not None:
        user.province = province
    if occupation is not None:
        user.occupation = occupation
    if bio is not None:
        user.bio = bio
    if tags is not None:
        user.tags = json.dumps(tags, ensure_ascii=False)
    await db.commit()
    await db.refresh(user)
    return user


async def change_password(
    db: AsyncSession, user: User, *, old_password: str, new_password: str
) -> bool:
    if not verify_password(old_password, user.password_hash):
        return False
    user.password_hash = hash_password(new_password)
    await db.commit()
    return True


async def list_users(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    role: str | None = None,
) -> tuple[list[User], int]:
    base = select(User).where(User.is_deleted == 0)
    if keyword:
        like = f"%{keyword}%"
        base = base.where(
            or_(
                User.username.ilike(like),
                User.nickname.ilike(like),
                User.platform_id.ilike(like),
                User.phone.ilike(like),
            )
        )
    if role:
        base = base.where(User.role == role)

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    items_stmt = base.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(items_stmt)).scalars().all()
    return list(items), total


async def search_users(
    db: AsyncSession,
    *,
    keyword: str,
    limit: int = 10,
) -> list[User]:
    like = f"%{keyword}%"
    stmt = (
        select(User)
        .where(
            User.is_deleted == 0,
            User.is_locked == 0,
            or_(
                User.nickname.ilike(like),
                User.platform_id.ilike(like),
                User.username.ilike(like),
            ),
        )
        .order_by(User.created_at.desc())
        .limit(limit)
    )
    items = (await db.execute(stmt)).scalars().all()
    return list(items)


async def admin_update_user(
    db: AsyncSession,
    user: User,
    *,
    nickname: str | None = None,
    role: str | None = None,
    province: str | None = None,
    occupation: str | None = None,
    bio: str | None = None,
    tags: list[str] | None = None,
) -> User:
    if nickname is not None:
        user.nickname = nickname
    if role is not None:
        user.role = role
    if province is not None:
        user.province = province
    if occupation is not None:
        user.occupation = occupation
    if bio is not None:
        user.bio = bio
    if tags is not None:
        user.tags = json.dumps(tags, ensure_ascii=False)
    await db.commit()
    await db.refresh(user)
    return user


async def lock_user(db: AsyncSession, user: User) -> User:
    user.is_locked = 1
    await db.commit()
    await db.refresh(user)
    return user


async def unlock_user(db: AsyncSession, user: User) -> User:
    user.is_locked = 0
    await db.commit()
    await db.refresh(user)
    return user
