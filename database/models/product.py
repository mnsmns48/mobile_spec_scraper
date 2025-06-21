from datetime import datetime
from typing import Annotated, Optional

from sqlalchemy import DateTime, func, UniqueConstraint, Index, text, Computed, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSON, TSVECTOR, ARRAY, JSONB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import event

from database.models.base import Base

pk = Annotated[str, mapped_column(primary_key=True)]
datetime_obj = Annotated[datetime, mapped_column(DateTime(timezone=False), server_default=func.now())]
info_obj = Annotated[dict, mapped_column(type_=JSONB)]


class Product(Base):
    __table_args__ = (
        UniqueConstraint('link', name='uix_link'),
        Index('idx_link', 'link'),
        Index('idx_title_tsv', 'title_tsv', postgresql_using='gin'),
    )
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title_line: Mapped[str]
    title: Mapped[str]
    title_tsv: Mapped[TSVECTOR] = mapped_column(TSVECTOR, Computed("to_tsvector('simple', title)", persisted=True))
    brand_id: Mapped[int] = mapped_column(ForeignKey('brand.id'), nullable=True)
    product_type_id: Mapped[int] = mapped_column(ForeignKey('product_type.id'), nullable=True)
    link: Mapped[str]
    source: Mapped[str]
    info: Mapped[info_obj]
    pros_cons: Mapped[Optional[info_obj]]
    create: Mapped[datetime] = mapped_column(DateTime(timezone=False))
    update: Mapped[datetime_obj]
    product_type: Mapped['Product_Type'] = relationship('Product_Type', back_populates='products')
    brand: Mapped['Brand'] = relationship('Brand', back_populates='products')


class Product_Type(Base):
    __table_args__ = (
        Index('idx_kind_tsv', 'kind_tsv', postgresql_using='gin'),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(nullable=False)
    kind: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    kind_tsv: Mapped[TSVECTOR] = mapped_column(TSVECTOR, nullable=True)
    products: Mapped[list['Product']] = relationship('Product', back_populates='product_type')


class Brand(Base):
    __table_args__ = (
        Index('idx_brand_depends_tsv', 'brand_depends_tsv', postgresql_using='gin'),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(nullable=False)
    brand_depends: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    brand_depends_tsv: Mapped[TSVECTOR] = mapped_column(TSVECTOR, nullable=True)
    products: Mapped[list['Product']] = relationship('Product', back_populates='brand')


@event.listens_for(Product_Type.__table__, "after_create")
def create_product_type_trigger(target, connection, **kw):
    connection.execute(text("""
        CREATE OR REPLACE FUNCTION update_kind_tsv_function() RETURNS TRIGGER AS $$
        BEGIN
            NEW.kind_tsv := to_tsvector('simple', array_to_string(NEW.kind, ' '));
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """))

    connection.execute(text("""
        CREATE TRIGGER tsvectorupdate_product_type BEFORE INSERT OR UPDATE
        ON product_type
        FOR EACH ROW
        EXECUTE FUNCTION update_kind_tsv_function();
        """))


@event.listens_for(Brand.__table__, "after_create")
def create_brand_trigger(target, connection, **kw):
    connection.execute(text("""
        CREATE OR REPLACE FUNCTION update_brand_depends_tsv_function() RETURNS TRIGGER AS $$
        BEGIN
            NEW.brand_depends_tsv := to_tsvector('simple', array_to_string(NEW.brand_depends, ' '));
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """))

    connection.execute(text("""
        CREATE TRIGGER tsvectorupdate_brand BEFORE INSERT OR UPDATE
        ON brand
        FOR EACH ROW
        EXECUTE FUNCTION update_brand_depends_tsv_function();
        """))


@event.listens_for(Product.__table__, "after_create")
def create_product_trigger(target, connection, **kw):
    connection.execute(text("""
        CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
        ON product FOR EACH ROW EXECUTE PROCEDURE
        tsvector_update_trigger(title_tsv, 'pg_catalog.simple', title);
        """))
