from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class IdIntPkMixin:
    id: Mapped[int] = mapped_column(primary_key=True)


class AdditionalUserFields:
    phone_number: Mapped[int]
    vk_id: Mapped[int] = mapped_column(nullable=True)
    full_name: Mapped[str] = mapped_column(nullable=True)
    birthday: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=True)
    address: Mapped[int] = mapped_column(nullable=True)
