from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .. import Base, Source

class Target(Base):

    __tablename__ = 'targets'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=True)
    name: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column(String(50))
 

    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    source: Mapped["Source"] = relationship("Source", foreign_keys=[source_id], lazy="selectin")
    skip_media: Mapped[bool] =  mapped_column(nullable=True, default=False)

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "base"
    }