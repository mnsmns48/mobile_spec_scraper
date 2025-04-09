from sqlalchemy.orm import mapped_column, Mapped

from database.models.base import Base


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)