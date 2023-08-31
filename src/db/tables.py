from sqlalchemy import DateTime, Float, Text, ARRAY, Uuid, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from zoneinfo import ZoneInfo

def timenow():
    return datetime.now(tz=ZoneInfo("America/New_York"))

class BaseTable(DeclarativeBase):
    created_on:Mapped[datetime] = mapped_column(DateTime(timezone=True), default=timenow)
    updated_on:Mapped[datetime] = mapped_column(DateTime(timezone=True), default=timenow)
    updated_by:Mapped[str] = mapped_column(Text, nullable=False)
    created_by:Mapped[str] = mapped_column(Text, nullable=False)
    sys_notes:Mapped[Optional[str]] = mapped_column(Text)


class ConfigTypes(BaseTable):
    __tablename__ = "configtypes"

    id:Mapped[UUID] = mapped_column(Uuid(native_uuid=True), server_default=func.gen_random_uuid(), primary_key=True)
    value:Mapped[str] = mapped_column(Text, nullable=False)
    name:Mapped[str] = mapped_column(Text,nullable=False)
    relations:Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    belongs_to:Mapped[str] = mapped_column(Text, nullable=False)
    description:Mapped[Optional[str]] = mapped_column(Text)
    status:Mapped[str] = mapped_column(Text, nullable=False)


class Expense(BaseTable):
    __tablename__ = "expenses"

    id:Mapped[UUID] = mapped_column(Uuid(native_uuid=True), server_default=func.gen_random_uuid(), primary_key=True)
    parent_expense_id:Mapped[Optional[UUID]] = mapped_column(ForeignKey("expenses.id", ondelete="CASCADE"), nullable=True)
    billname:Mapped[str] = mapped_column(Text, nullable=False)
    amount:Mapped[Optional[float]] = mapped_column(Float)
    payment_account:Mapped[Optional[str]] = mapped_column(Text)
    description:Mapped[Optional[str]] = mapped_column(Text)
    purchased_date:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    tags:Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    verified_date_time:Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    category_id:Mapped[Optional[UUID]] = mapped_column(ForeignKey("configtypes.id"), nullable=True)


class Account(BaseTable):
    __tablename__ = "accounts"

    id:Mapped[UUID] = mapped_column(Uuid(native_uuid=True), server_default=func.gen_random_uuid(), primary_key=True)
    account_number:Mapped[Optional[str]] = mapped_column(Text)
    short_name:Mapped[str] = mapped_column(Text, nullable=False)
    account_name:Mapped[Optional[str]] = mapped_column(Text)
    type_id:Mapped[Optional[UUID]] = mapped_column(ForeignKey("configtypes.id"), nullable=True)
    tags:Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    institution_name:Mapped[Optional[str]] = mapped_column(Text)
    description:Mapped[Optional[str]] = mapped_column(Text)


class User(BaseTable):
    __tablename__ = "users"

    id:Mapped[UUID] = mapped_column(Uuid(native_uuid=True), server_default=func.gen_random_uuid(), primary_key=True)
    username:Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    password:Mapped[str] = mapped_column(Text, nullable=False)
    encrypt_type:Mapped[str] = mapped_column(Text, nullable=False)
    email_id:Mapped[Optional[str]] = mapped_column(Text)
    phone_number:Mapped[Optional[str]] = mapped_column(Text)


