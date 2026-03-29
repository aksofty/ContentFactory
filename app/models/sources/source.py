import enum
from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .. import Base

class Source(Base):

    __tablename__ = 'sources'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=True)
    name: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column(String(50))
    cron: Mapped[str] = mapped_column(default="* 1 * * *") 
    limit: Mapped[int] = mapped_column(default=1)

    allowed_filter_id: Mapped[int] = mapped_column(ForeignKey("filters.id"), nullable=True)
    forbidden_filter_id: Mapped[int] = mapped_column(ForeignKey("filters.id"), nullable=True)
    ai_prompt_id: Mapped[int] = mapped_column(ForeignKey("ai_prompts.id"), nullable=True)

    allowed_filter: Mapped["Filter"] = relationship("Filter", foreign_keys=[allowed_filter_id], lazy="selectin")
    forbidden_filter: Mapped["Filter"] = relationship("Filter", foreign_keys=[forbidden_filter_id], lazy="selectin")
    ai_prompt: Mapped["AIPrompt"] = relationship("AIPrompt", foreign_keys=[ai_prompt_id], lazy="selectin")

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "base"
    }

class Filter(Base):
    __tablename__ = 'filters'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    keywords: Mapped[str] = mapped_column(Text, nullable=False)


# AI
class AiModel(enum.Enum):
    GEMINI25_FLASH = "gemini-2-5-flash"
    GEMINI25_FLASH_LITE = "gemini-2-5-flash-lite"
    GEMINI25_PRO = "gemini-2-5-pro"
    GHATGPT_3 = "chat-gpt-3"
    GHATGPT_4_O_MINI = "gpt-4o-mini"


class AIPrompt(Base):
    __tablename__ = 'ai_prompts'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    ai_model: Mapped[AiModel] = mapped_column(Enum(AiModel), default=AiModel.GEMINI25_FLASH_LITE)

