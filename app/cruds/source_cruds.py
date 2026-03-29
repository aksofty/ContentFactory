from sqlalchemy import select
from sqlalchemy.orm import with_polymorphic
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sources.source import Source
from app.models.sources.source_tg import SourceTg
from app.models.sources.source_rss import SourceRss

async def get_source_list(session: AsyncSession, is_active: bool|None = None):
    stmt = select(with_polymorphic(Source, [SourceTg, SourceRss])) 
    if is_active is not None:
        stmt = stmt.where(Source.is_active == is_active)
    result = await session.execute(stmt)
    return result.scalars().all()

async def get_source(session: AsyncSession, id: int):
    entity = with_polymorphic(Source, [SourceTg, SourceRss])
    query = select(entity).where(entity.id == id)
    result = await session.execute(query)
    return result.scalar_one_or_none()