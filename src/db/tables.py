from sqlalchemy import DateTime, Float, Text, ARRAY, Uuid, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID
from zoneinfo import ZoneInfo
from utils import SerializeModel
import logging


logger = logging.getLogger(__name__)


def timenow():
    return datetime.now(tz=ZoneInfo("America/New_York"))


class BaseTable(DeclarativeBase):
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=timenow)
    updated_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=timenow)
    updated_by: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str] = mapped_column(Text, nullable=False)
    sys_notes: Mapped[Optional[str]] = mapped_column(Text)

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_model(cls, model: SerializeModel):
        model_dict = model.model_dump(by_alias=True)
        logger.debug("model dumped to dictionary: " + str(model_dict))
        db_record = cls(**model_dict)
        return db_record

    def update_entry(self, entry: DeclarativeBase):
        difference(entry.__dict__, self.__dict__)
        self.__dict__.update(entry.__dict__)
        difference(entry.__dict__, self.__dict__)


def difference(dict1: Dict, dict2: Dict):
    for k, v in dict1.items():
        if k in dict2:
            if v != dict2[k]:
                logger.debug(f"value is different in dict2, dict1 item has key [{k}] and \
                         value [{v}], but dict2 value [{dict2[k]}]")
    missing_keys(dict1, dict2)


def missing_keys(dict1: Dict, dict2: Dict):
    for k, v in dict1.items():
        if k not in dict2:
            logger.debug(f"key not found in dict2, dict1 item has key [{k}] and \
                    value [{v}]")
    for k, v in dict2.items():
        if k not in dict1:
            logger.debug(f"key not found in dict1, dict2 item has key [{k}] and \
                    value [{v}]")


class ConfigTypes(BaseTable):
    __tablename__ = "configtypes"

    id: Mapped[UUID] = mapped_column(
        Uuid(native_uuid=True), server_default=func.gen_random_uuid(), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    relations: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    belongs_to: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False)


class Expense(BaseTable):
    __tablename__ = "expenses"

    id: Mapped[UUID] = mapped_column(
        Uuid(native_uuid=True), server_default=func.gen_random_uuid(), primary_key=True)
    parent_expense_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("expenses.id", ondelete="CASCADE"), nullable=True)
    billname: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Optional[float]] = mapped_column(Float)
    payment_account: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    purchased_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    tags: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    verified_date_time: Mapped[Optional[datetime]
                               ] = mapped_column(DateTime(timezone=True))
    category_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("configtypes.id"), nullable=True)


class Account(BaseTable):
    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column(
        Uuid(native_uuid=True), server_default=func.gen_random_uuid(), primary_key=True)
    account_number: Mapped[Optional[str]] = mapped_column(Text)
    short_name: Mapped[str] = mapped_column(Text, nullable=False)
    account_name: Mapped[Optional[str]] = mapped_column(Text)
    type_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("configtypes.id"), nullable=True)
    tags: Mapped[List[str]] = mapped_column(ARRAY(Text), nullable=False)
    institution_name: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)


class User(BaseTable):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        Uuid(native_uuid=True), server_default=func.gen_random_uuid(), primary_key=True)
    username: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    encrypt_type: Mapped[str] = mapped_column(Text, nullable=False)
    email_id: Mapped[Optional[str]] = mapped_column(Text)
    phone_number: Mapped[Optional[str]] = mapped_column(Text)
