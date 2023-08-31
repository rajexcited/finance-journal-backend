from typing import List, Dict, Optional
import logging
from db.base import alchemy_engine
from rest.resource import ConfigTypeQueryModel, ExpenseResource, ConfigTypeResource
from sqlalchemy.orm import Session
from sqlalchemy import select
from db.tables import Expense as DBExpense
from db.tables import ConfigTypes as DBConfigTypes


logger = logging.getLogger(__name__)


def get_expenses() -> List[ExpenseResource]:
    expense_list = []
    with Session(alchemy_engine) as session:
        for item in session.query(DBExpense):
            logger.debug("db expense dictionary")
            logger.debug(item.__dict__)
            item_resource = ExpenseResource.model_validate(item.__dict__)
            expense_list.append(item_resource)
    return expense_list


def add_expense(exp: ExpenseResource):
    logger.debug("exp in request")
    logger.debug(exp)
    with Session(alchemy_engine) as session:
        expense_dict = exp.model_dump(by_alias=True)
        logger.debug("expense dict")
        logger.debug(expense_dict)
        expense = DBExpense(**expense_dict)
        logger.debug("db expense")
        logger.debug(expense.__dict__)
        session.add(expense)
        session.commit()


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
        for k,v in ctype:
            setattr(conf_type,k, v)
        session.commit()
    return True


def updated_query_dict(query:Dict[str, str]):
    qq = query.copy()
    for k,v in query.items():
        if not v:
            del qq[k]
    return qq

