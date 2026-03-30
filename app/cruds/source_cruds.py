from sqlalchemy import select
from sqlalchemy.orm import with_polymorphic
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sources.source import Source
from app.models.sources.source_tg import SourceTg
from app.models.sources.source_rss import SourceRss

async def get_source_list(session: AsyncSession, is_active: bool|None = None, populate_existing=True):
    stmt = select(with_polymorphic(Source, [SourceTg, SourceRss])) 
    if is_active is not None:
        stmt = stmt.where(Source.is_active == is_active)
    if populate_existing:
        stmt = stmt.execution_options(populate_existing=True)

    result = await session.execute(stmt)
    return result.scalars().all()

async def get_source(session: AsyncSession, id: int, populate_existing=True):
    entity = with_polymorphic(Source, [SourceTg, SourceRss])
    stmt = select(entity).where(entity.id == id)
    if populate_existing:
        stmt = stmt.execution_options(populate_existing=True)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()