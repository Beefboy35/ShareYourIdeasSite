
from uuid import uuid4

from sqlalchemy import ForeignKey, UniqueConstraint, UUID, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase



class Base(DeclarativeBase):
    pass

class Idea(Base):
    __tablename__ = "ideas"
    idea_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False, server_default="None")
    updated_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"),nullable=False)
    nickname: Mapped[str] = mapped_column(String, nullable=False, server_default="dummy")
    user: Mapped["User"] = relationship("User", back_populates="ideas")

    __table_args__ = (
    UniqueConstraint('idea_id', 'user_id', name='uc_idea_user'),)



class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    nickname: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP(timezone=True), nullable=False,
                                              server_default=text("now()"))
    role: Mapped[str] = mapped_column(String,nullable=False, server_default="user")
    avatar_filename: Mapped[str] = mapped_column(String, nullable=True)



    ideas: Mapped[list["Idea"]] = relationship("Idea", back_populates="user")


