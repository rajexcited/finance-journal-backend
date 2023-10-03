from typing import List, Dict, Optional
import logging
from db.base import alchemy_engine
from rest.resource import ConfigTypeQueryModel, FilterByIdQueryModel
from rest.expense_service import ExpenseResource
from rest.config_types_service import ConfigTypeResource
from rest.account_service import AccountResource
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from db.tables import (
    Expense as DBExpense,
    ConfigTypes as DBConfigTypes,
    Account as DBAccount
)


logger = logging.getLogger(__name__)


def get_expenses() -> List[ExpenseResource]:
    logger.debug("entering get_expenses method")
    expense_list = []
    with Session(alchemy_engine) as session:
        for item in session.query(DBExpense):
            item_resource = ExpenseResource.model_validate(item.__dict__)
            expense_list.append(item_resource)
    logger.debug("entering get_expenses method")
    return expense_list


def add_expense(exp: ExpenseResource):
    logger.debug("entering add_expense method")
    with Session(alchemy_engine) as session:
        expense_dict = exp.model_dump(by_alias=True)
        expense = DBExpense(**expense_dict)
        session.add(expense)
        session.commit()
        logger.info("added expense to DB:  " + str(expense.id))
        returning_expense = get_expense(
            FilterByIdQueryModel(id=expense.id), session)

    logger.debug("exiting add_expense method")
    return returning_expense


def update_expense(exp: ExpenseResource):
    logger.debug("entering update_expense method")
    with Session(alchemy_engine) as session:
        expense_dict = exp.model_dump(by_alias=True)
        expense = DBExpense(**expense_dict)
        stmt = select(DBExpense).filter_by(id=exp.expenseId)
        db_expense = session.scalar(stmt)
        if not db_expense:
            logger.info("expense not found in DB, so adding new one")
            del expense.id
            session.add(expense)
        else:
            logger.info("expense found in DB, so updating")
            db_expense.__dict__.update(expense.__dict__)
        session.commit()
        returning_expense = get_expense(
            FilterByIdQueryModel(id=expense.id), session)
    logger.debug("exiting update_expense method")
    return returning_expense


def get_expense(query: FilterByIdQueryModel, session: Session):
    logger.debug("entering get_expense method")
    stmt = select(DBExpense).filter_by(id=query.id)
    db_expense = session.scalar(stmt)
    expense_resource = ExpenseResource.model_validate(db_expense.__dict__)
    logger.debug("exiting get_expense method")
    return expense_resource


def delete_expense(expense_id: str):
    logger.debug("entering delete_expense method")
    with Session(alchemy_engine) as session:
        expense = get_expense(FilterByIdQueryModel(id=expense_id), session)
        stmt = delete(DBExpense).filter_by(id=expense_id)
        result = session.execute(stmt)
        logger.debug("executed delete statement, result: " +
                     str(result.__dict__))
        session.commit()
    logger.debug("exiting delete_expense method")
    return expense


def get_accounts() -> List[AccountResource]:
    account_list = []
    with Session(alchemy_engine) as session:
        for item in session.query(DBAccount):
            item_resource = AccountResource.model_validate(item.__dict__)
            account_list.append(item_resource)
    return account_list


def add_account(acc: AccountResource):
    logger.debug("entering add_account method")
    with Session(alchemy_engine) as session:
        account_dict = acc.model_dump(by_alias=True)
        account = DBAccount(**account_dict)
        session.add(account)
        session.commit()
    logger.debug("exiting add_account method")


def update_account(acc: AccountResource):
    logger.debug("entering update_account method")
    if not acc.accountId:
        return add_account(acc)

    with Session(alchemy_engine) as session:
        account_dict = acc.model_dump(by_alias=True)
        account = DBAccount(**account_dict)
        stmt = select(DBAccount).filter_by(id=acc.accountId)
        db_account = session.scalar(stmt)
        if not db_account:
            del account.id
            session.add(account)
        else:
            db_account.__dict__.update(account.__dict__)
        session.commit()
    logger.debug("exiting update_expense method")


def get_config_types(query: ConfigTypeQueryModel, session: Optional[Session] = None):
    query_dict = updated_query_dict(query.model_dump(by_alias=True))
    stmt = select(DBConfigTypes).filter_by(**query_dict)
    config_types = []
    with Session(alchemy_engine) as session:
        for item in session.scalars(stmt):
            item_resource = ConfigTypeResource.model_validate(item.__dict__)
            config_types.append(item_resource)
    return config_types


def add_config_type(ctype: ConfigTypeResource):
    with Session(alchemy_engine) as session:
        conf_type_dict = ctype.model_dump(by_alias=True)
        config_type = DBConfigTypes(**conf_type_dict)
        session.add(config_type)
        session.commit()
        return config_type.id


def update_config_type(ctype: ConfigTypeResource):
    with Session(alchemy_engine) as session:
        conf_type = session.query(DBConfigTypes).get(ctype.configId)
        if not conf_type:
            return False
        for k, v in ctype:
            setattr(conf_type, k, v)
        session.commit()
    return True


def updated_query_dict(query: Dict[str, str]):
    qq = query.copy()
    for k, v in query.items():
        if not v:
            del qq[k]
    return qq
