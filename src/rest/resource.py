import logging
from pydantic import Field
from utils import SerializeModel
from typing import List, Optional, Dict, Union
from datetime import datetime
from uuid import UUID
from db.tables import BaseTable

logger = logging.getLogger(__name__)

UUID_VALIDATE_PATTERN: str = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'


class BaseResource(SerializeModel):
    createdBy: Optional[str] = Field(alias="created_by", default="dummy")
    updatedBy: Optional[str] = Field(alias="updated_by", default="dummy")
    createdOn: Optional[datetime] = Field(alias="created_on", default=None)
    updatedOn: Optional[datetime] = Field(alias="updated_on", default=None)

    def __init__(self, typechangelist: List[Dict[str, str]] = [], **kwargs):
        """
        """
        logger.debug(typechangelist)
        logger.debug("expense resource init kwargs")
        logger.debug(kwargs.items())
        args = {}
        kwargs_copy = kwargs.copy()
        for item in kwargs_copy.items():
            for tc in typechangelist:
                if item[0] == tc['uuidcolumn'] or item[0] == tc["strattr"]:
                    kwargs.pop(item[0])
                    args[item[0]] = item[1]

        logger.debug(f"args built: {args}")
        for k, v in args.items():
            logger.debug(f"k={k} and v={v}")
            if isinstance(v, UUID):
                args[k] = str(v)
            elif v:
                args[k] = UUID(v)

        if len(args) > 0:
            logger.debug(f"args: {str(args)} and  kwargs: {str(kwargs)}")
            super().__init__(**args, **kwargs)
        else:
            logger.debug(f"kwargs: {str(kwargs)}")
            super().__init__(**kwargs)

    @classmethod
    def from_db_entry(cls, db_entry: BaseTable):
        logger.debug("table entry dictionary: " + str(db_entry.to_dict()))
        resource = cls.model_validate(db_entry.to_dict())
        return resource


class ConfigTypeQueryModel(SerializeModel):
    belongsTo: Optional[str] = Field(alias="belongs_to", default=None)
    configId: Optional[str] = Field(alias="id", default=None)
    status: Optional[str] = None


class FilterByIdQueryModel(SerializeModel):
    id: Optional[Union[str, UUID]] = None


class BaseFilterQueryModel(SerializeModel):
    id: Optional[str] = None
    name: Optional[str] = None
    fromDate: Optional[datetime] = None
    toDate: Optional[datetime] = None
    all: Optional[bool] = None
    pageNumber: Optional[int] = None
    pageSize: Optional[int] = None
