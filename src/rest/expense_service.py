from typing import List, Optional, Union
import logging
from uuid import UUID
from pydantic import Field
from datetime import datetime
from utils import SerializeModel
from db.base import alchemy_engine
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from rest.resource import BaseResource
from db.tables import Expense as DBExpense


logger = logging.getLogger(__name__)


class ExpenseResource(BaseResource):
    """Expense Details"""
    expenseId: Optional[Union[str, UUID]] = Field(alias="id", default=None)
    billname: str
    amount: Optional[float] = None
    paymentAccount: Optional[str] = Field(
        alias="payment_account", default=None)
    description: Optional[str] = None
    purchasedDate: datetime = Field(alias="purchased_date", default=None)
    tags: List[str] = []
    verifiedDateTime: Optional[datetime] = Field(
        alias="verified_date_time", default=None)
    parentExpenseId: Optional[str] = Field(
        alias="parent_expense_id", default=None)
    categoryId: Optional[str] = Field(alias="category_id", default=None)

    def __init__(self, **kwargs):
        typechanges = [
            {"uuidcolumn": "id", "strattr": "expenseId"},
            {"uuidcolumn": "parent_expense_id", "strattr": "parentExpenseId"},
            {"uuidcolumn": "category_id", "strattr": "categoryId"}
        ]
        logger.info("ExpenseResource: " + str(kwargs))
        super().__init__(typechangelist=typechanges, **kwargs)


class ExpenseService(SerializeModel):
    """Rest Service to support the add, update, delete, filter, etc."""

    def get_expenses(self) -> List[ExpenseResource]:
        """retrieves all expenses"""
        logger.debug("entering method")
        expense_list = []
        with Session(alchemy_engine) as session:
            expense_list = [
                ExpenseResource.from_db_entry(db_item) for db_item in session.query(DBExpense)
            ]
        logger.debug("exiting method")
        return expense_list

    def add_expense(self, expense: ExpenseResource) -> ExpenseResource:
        """inserts an expense"""
        logger.debug("entering method")
        with Session(alchemy_engine) as session:
            db_expense = DBExpense.from_model(expense)
            session.add(db_expense)
            session.commit()
            logger.info("added expense to DB:  " + str(db_expense.id))
            returning_expense = self.get_expense(db_expense.id, session)
        logger.debug("exiting method")
        if returning_expense:
            return returning_expense
        raise ValueError(
            "this should never be executed, since entry has just been added")

    def update_expense(self, expense: ExpenseResource) -> ExpenseResource:
        """ updates an existing expense or insert an expense"""
        logger.debug("entering method")
        assert expense.expenseId, "expenseId must be provided"
        with Session(alchemy_engine) as session:
            db_expense = DBExpense.from_model(expense)
            stmt = select(DBExpense).filter_by(id=expense.expenseId)
            found_db_expense = session.scalar(stmt)
            if not found_db_expense:
                logger.info("expense not found in DB, so adding new one")
                del db_expense.id
                session.add(db_expense)
            else:
                logger.info("expense found in DB, so updating")
                found_db_expense.update_entry(db_expense)
            returning_expense = self.get_expense(db_expense.id, session)
            session.commit()
        logger.debug("exiting method")
        if returning_expense:
            return returning_expense
        raise ValueError(
            "this should never be executed, since existing entry has just been updated")

    def get_expense(self, expense_id: Union[str, UUID], session: Session) -> Optional[ExpenseResource]:
        """retrieves an expense"""
        logger.debug("entering method")
        logger.debug("type of expense_id: " + str(type(expense_id))
                     + ", value: " + str(expense_id))
        if isinstance(expense_id, UUID):
            id = expense_id
        else:
            id = UUID(expense_id)
        stmt = select(DBExpense).filter_by(id=id)
        db_expense = session.query(DBExpense).filter_by(id=expense_id).first()
        logger.debug("exiting method")
        if db_expense:
            logger.debug("before converting, db_expense: " +
                         str(db_expense.to_dict()))
            return ExpenseResource.from_db_entry(db_expense)
        return None

    def delete_expense(self, expense_id: str) -> Optional[ExpenseResource]:
        """deletes an expense"""
        logger.debug("entering method")
        with Session(alchemy_engine) as session:
            expense = self.get_expense(expense_id, session)
            stmt = delete(DBExpense).filter_by(id=expense_id)
            result = session.execute(stmt)
            logger.info("executed delete statement, result: " +
                        str(result.__dict__))
            session.commit()
        logger.debug("exiting method")
        return expense
