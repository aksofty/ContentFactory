from sqlalchemy import select, update
from sqlalchemy.orm import with_polymorphic
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.targets.target import Target
from app.models.targets.target_tg import TargetTg

async def get_target_list(session: AsyncSession, source_id: int|None=None, is_active: bool|None = None):
    stmt = select(with_polymorphic(Target, [TargetTg])) 
    if is_active:
        stmt = stmt.where(Target.is_active == is_active)
    if source_id:
        stmt = stmt.where(Target.source_id == source_id)

    result = await session.execute(stmt)
    return result.scalars().all()

async def get_target(session: AsyncSession, id: int):
    entity = with_polymorphic(Target, [TargetTg])
    query = select(entity).where(entity.id == id)
    result = await session.execute(query)
    return result.scalar_one_or_none()