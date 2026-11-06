import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    role = Column(String, default="teacher")  # 'admin', 'teacher', or 'operator'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __init__(self, **kwargs):
        if "hashed_password" in kwargs and "password_hash" not in kwargs:
            kwargs["password_hash"] = kwargs.pop("hashed_password")
        super().__init__(**kwargs)

    @property
    def hashed_password(self):
        return self.password_hash

    @hashed_password.setter
    def hashed_password(self, val):
        self.password_hash = val


# Aliases for bidirectional compatibility
UserModel = User

