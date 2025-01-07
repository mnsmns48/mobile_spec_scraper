from datetime import datetime
from typing import Annotated, Optional

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import DeclarativeBase, declared_attr, mapped_column, Mapped

title_pk = Annotated[str, mapped_column(primary_key=True, unique=True)]
brand_pk = Annotated[str, mapped_column(primary_key=True)]
datetime_obj = Annotated[datetime, mapped_column(DateTime(timezone=False), server_default=func.now())]
link_obj = Annotated[str, mapped_column(unique=True)]
info_obj = Annotated[dict, mapped_column(type_=JSON)]


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Specification(Base):
    title: Mapped[title_pk]
    brand: Mapped[brand_pk]
    link: Mapped[link_obj]
    source: Mapped[str]
    info: Mapped[info_obj]
    pros_cons: Mapped[Optional[info_obj]]
    create: Mapped[datetime] = mapped_column(DateTime(timezone=False))
    update: Mapped[datetime_obj]
