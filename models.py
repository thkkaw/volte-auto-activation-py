from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db import Base

class OfferCode(Base):
    __tablename__ = "offer_codes"

    id: Mapped[int] = mapped_column(primary_key=True)

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )