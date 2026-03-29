from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ..import Target

class TargetTg(Target):
    __tablename__ = 'targets_tg'

    id: Mapped[int] = mapped_column(ForeignKey("targets.id"), primary_key=True)

    channel: Mapped[str] = mapped_column(nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "tg"
    }
