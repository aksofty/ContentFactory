from sqlalchemy import select, update
from sqlalchemy.orm import selectinload, with_polymorphic
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.targets.target import Target
from app.models.targets.target_tg import TargetTg
from app.models.targets.target_vk import TargetVK

async def get_target_list(session: AsyncSession, source_id: int|None=None, is_active: bool|None = None, populate_existing=True):
    stmt = select(with_polymorphic(Target, [TargetTg, TargetVK])) 
    if is_active:
        stmt = stmt.where(Target.is_active == is_active)
    if source_id:
        stmt = stmt.where(Target.source_id == source_id)
    if populate_existing:
        stmt = stmt.execution_options(populate_existing=True)

    stmt = stmt.options(selectinload('*'))

    result = await session.execute(stmt)
    return result.scalars().all()

async def get_target(session: AsyncSession, id: int, populate_existing=True):
    entity = with_polymorphic(Target, [TargetTg, TargetVK])
    stmt = select(entity).where(entity.id == id)
    if populate_existing:
        stmt = stmt.execution_options(populate_existing=True)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()