from sqlalchemy import Column, String, Integer, Index, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime

from app.core.database import Base


class Company(Base):
	__tablename__="companies"

	id: Mapped[int]=mapped_column(primary_key=True)
	name: Mapped[str]=mapped_column(String(255), unique=True, nullable=False)
	created_at: Mapped[datetime] = mapped_column(
	    DateTime,
	    default=datetime.utcnow,
	    nullable=False,
	)

	questions: Mapped[list["Question"]] = relationship(back_populates="company")
