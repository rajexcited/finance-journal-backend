from pydantic import Field
from typing import List, Optional, Union
import logging
from db.base import alchemy_engine
from rest.resource import BaseResource
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from db.tables import Account as DBAccount
from utils import SerializeModel
from uuid import UUID


logger = logging.getLogger(__name__)


class AccountResource(BaseResource):
    """Account Details """
    accountId: Optional[str] = Field(alias="id", default=None)
    accountNumber: Optional[str] = Field(alias="account_number", default=None)
    shortName: str = Field(alias="short_name")
    accountName: Optional[str] = Field(alias="account_name", default=None)
    typeId: Optional[str] = Field(alias="type_id", default=None)
    """this is in corelated to AccountType resource, the value must be accountTypeId"""
    tags: List[str] = []
    institutionName: Optional[str] = Field(
        alias="institution_name", default=None)
    description: Optional[str] = None

    def __init__(self, **kwargs):
        typechanges = [
            {"uuidcolumn": "id", "strattr": "accountId"},
            {"uuidcolumn": "type_id", "strattr": "typeId"}
        ]
        super().__init__(typechangelist=typechanges, **kwargs)


class AccountService(SerializeModel):
    """Rest Service to support the add, update, delete, filter, etc."""

    def get_accounts(self) -> List[AccountResource]:
        """retrieves all accounts"""
        logger.debug("entering method")
        account_list = []
        with Session(alchemy_engine) as session:
            account_list = [
                AccountResource.from_db_entry(item) for item in session.query(DBAccount)
            ]
        logger.debug("exiting method")
        return account_list

    def add_account(self, account: AccountResource) -> AccountResource:
        """ inserts an account """
        logger.debug("entering method")
        with Session(alchemy_engine) as session:
            db_account = DBAccount.from_model(account)
            session.add(db_account)
            session.commit()
            returning_account = self.get_account(db_account.id, session)
        logger.debug("exiting method")
        if returning_account:
            return returning_account
        raise ValueError(
            "this should never be executed, since entry has just been added")

    def update_account(self, account: AccountResource) -> AccountResource:
        """ updates an existing account or inserts an account """
        logger.debug("entering method")
        assert account.accountId, "accountId must be provided"
        with Session(alchemy_engine) as session:
            db_account = DBAccount.from_model(account)
            stmt = select(DBAccount).filter_by(id=account.accountId)
            found_db_account = session.scalar(stmt)
            if not found_db_account:
                logger.info("account not found in DB, so adding new one")
                del db_account.id
                session.add(db_account)
            else:
                logger.info("account found in DB, so updating")
                found_db_account.update_entry(db_account)
            returning_account = self.get_account(db_account.id, session)
            session.commit()
        logger.debug("exiting method")
        if returning_account:
            return returning_account
        raise ValueError(
            "this should never be executed, since existing entry has just been updated")

    def get_account(self, account_id: Union[str, UUID], session: Session) -> Optional[AccountResource]:
        """retrieves an account"""
        logger.debug("entering method")
        stmt = select(DBAccount).filter_by(id=account_id)
        db_account = session.scalar(stmt)
        logger.debug("exiting method")
        if db_account:
            return AccountResource.from_db_entry(db_account)
        return None

    def delete_account(self, account_id: str) -> Optional[AccountResource]:
        """deletes an account"""
        logger.debug("entering method")
        with Session(alchemy_engine) as session:
            account = self.get_account(account_id, session)
            stmt = delete(DBAccount).filter_by(id=account_id)
            result = session.execute(stmt)
            logger.info("executed delete statement, result: " +
                        str(result.__dict__))
            session.commit()
        logger.debug("exiting method")
        return account
