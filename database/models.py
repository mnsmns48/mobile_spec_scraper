from datetime import datetime
from typing import Annotated, Optional

from sqlalchemy import DateTime, func, UniqueConstraint, Index, text, Computed
from sqlalchemy.dialects.postgresql import JSON, TSVECTOR
from sqlalchemy.orm import DeclarativeBase, declared_attr, mapped_column, Mapped
from sqlalchemy import event

pk = Annotated[str, mapped_column(primary_key=True)]
datetime_obj = Annotated[datetime, mapped_column(DateTime(timezone=False), server_default=func.now())]
info_obj = Annotated[dict, mapped_column(type_=JSON)]


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Devices(Base):
    __table_args__ = (UniqueConstraint('link', name='uix_link'),
                      Index('idx_link', 'link'),
                      Index('idx_title_tsv', 'title_tsv', postgresql_using='gin'))
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    title_tsv: Mapped[TSVECTOR] = mapped_column(TSVECTOR, Computed("to_tsvector('english', title)",
                                                                   persisted=True))
    brand: Mapped[str]
    product_type: Mapped[str | None]
    link: Mapped[str]
    source: Mapped[str]
    info: Mapped[info_obj]
    pros_cons: Mapped[Optional[info_obj]]
    create: Mapped[datetime] = mapped_column(DateTime(timezone=False))
    update: Mapped[datetime_obj]


@event.listens_for(Devices.__table__, 'after_create')
def create_update_title_tsv_trigger(target, connection, **kw):
    connection.execute(text(
        """
        CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
        ON devices FOR EACH ROW EXECUTE PROCEDURE
        tsvector_update_trigger(title_tsv, 'pg_catalog.english', title);
        """
    ))
