from typing import List, Optional, Union
import logging
from uuid import UUID
from utils import SerializeModel
from pydantic import Field
from db.base import alchemy_engine
from rest.resource import ConfigTypeQueryModel, BaseResource
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from db.tables import (
    ConfigTypes as DBConfigTypes,
)

logger = logging.getLogger(__name__)


class ConfigTypeResource(BaseResource):
    """this can be used for account type and expense category static list configuration"""
    configId: Optional[str] = Field(alias="id", default=None)
    value: str
    name: str
    relations: List[str] = []
    """account type is related to which category or categories. will be helpful in ui to display selection"""
    belongsTo: str = Field(alias="belongs_to")
    """indicator whether type belongs to expense category or account type"""
    description: Optional[str] = None
    status: str = "enable"

    def __init__(self, **kwargs):
        typechanges = [
            {"uuidcolumn": "id", "strattr": "configId"}
        ]
        super().__init__(typechangelist=typechanges, **kwargs)


class ConfigTypeService(SerializeModel):
    """Config Type details"""

    def get_config_types(self, query: ConfigTypeQueryModel):
        """retrieves config types by filtering query"""
        logger.debug("entering method")
        # query_dict = updated_query_dict(query.model_dump(by_alias=True))
        query_dict = query.model_dump(by_alias=True, exclude_none=True)
        logger.debug("query dict: " + str(query_dict))
        stmt = select(DBConfigTypes).filter_by(**query_dict)
        config_types = []
        with Session(alchemy_engine) as session:
            config_types = [
                ConfigTypeResource.from_db_entry(db_item) for db_item in session.scalars(stmt)
            ]
        logger.debug("exiting method")
        return config_types

    def add_config_type(self, conf_type: ConfigTypeResource) -> ConfigTypeResource:
        """inserts a config type"""
        logger.debug("entering method")
        with Session(alchemy_engine) as session:
            db_config_type = DBConfigTypes.from_model(conf_type)
            session.add(db_config_type)
            session.commit()
            returning_config_type = self.get_config_type(
                db_config_type.id, session)
        logger.debug("exiting method")
        if returning_config_type:
            return returning_config_type
        raise ValueError(
            "this should never be executed, since entry has just been added")

    def update_config_type(self, config_type: ConfigTypeResource) -> ConfigTypeResource:
        """updates an existing config type or inserts a config type"""
        logger.debug("entering method")
        assert config_type.configId, "configId must be provided"
        with Session(alchemy_engine) as session:
            db_config_type = DBConfigTypes.from_model(config_type)
            stmt = select(DBConfigTypes).filter_by(id=config_type.configId)
            found_db_config_type = session.scalar(stmt)
            if not found_db_config_type:
                logger.info("config type not found in DB, so adding new one")
                del db_config_type.id
                session.add(db_config_type)
            else:
                logger.info("config type found in DB, so updating")
                found_db_config_type.update_entry(db_config_type)
            returning_config_type = self.get_config_type(
                db_config_type.id, session)
            session.commit()
        logger.debug("exiting method")
        if returning_config_type:
            return returning_config_type
        raise ValueError(
            "this should never be executed, since entry has just been added")

    def get_config_type(self, config_type_id: Union[str, UUID], session: Session) -> Optional[ConfigTypeResource]:
        """retrieves a config type"""
        logger.debug("entering method")
        stmt = select(DBConfigTypes).filter_by(id=config_type_id)
        db_config_type = session.scalar(stmt)
        logger.debug("exiting method")
        if db_config_type:
            return ConfigTypeResource.from_db_entry(db_config_type)
        return None

    def delete_config_type(self, config_type_id: str) -> Optional[ConfigTypeResource]:
        """deletes a config type"""
        logger.debug("entering method")
        with Session(alchemy_engine) as session:
            config_type = self.get_config_type(config_type_id, session)
            stmt = delete(DBConfigTypes).filter_by(id=config_type_id)
            result = session.execute(stmt)
            logger.info("executed delete statement, result: " +
                        str(result.__dict__))
            session.commit()
        logger.debug("exiting method")
        return config_type


# def updated_query_dict(query: Dict[str, str]):
#     qq = query.copy()
#     for k, v in query.items():
#         if not v:
#             del qq[k]
#     return qq
