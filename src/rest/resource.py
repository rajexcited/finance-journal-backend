import logging
from pydantic import Field
from utils import SerializeModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


logger = logging.getLogger(__name__)


class BaseResource(SerializeModel):
    createdBy: Optional[str] = Field(alias="created_by", default="neelsheth")
    updatedBy: Optional[str] = Field(alias="updated_by", default="neelsheth")
    createdOn: Optional[datetime] = Field(alias="created_on", default=None)
    updatedOn: Optional[datetime] = Field(alias="updated_on", default=None)

    def __init__(self, typechangelist:List[Dict[str,str]] = [], **kwargs):
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
        for k,v in args.items():
            logger.debug(f"k={k} and v={v}")
            if isinstance(v, UUID):
                args[k] = str(v)
            elif v:
                args[k] = UUID(v)

        if len(args) > 0:
            super().__init__(**args,**kwargs)
        else:
            super().__init__(**kwargs)


class ExpenseResource(BaseResource):
    expenseId: Optional[str] = Field(alias="id", default=None)
    billname: str
    amount: Optional[float] = None
    paymentAccount: Optional[str] = Field(alias="payment_account", default=None)
    description: Optional[str] = None
    purchasedDate: datetime = Field(alias="purchased_date", default=None)
    tags: List[str] = []
    verifiedDateTime: Optional[datetime] = Field(alias="verified_date_time", default=None)
    parentExpenseId: Optional[str] = Field(alias="parent_expense_id", default=None)
    categoryId: Optional[str] = Field(alias="category_id", default=None)

    def __init__(self, **kwargs):
        typechanges = [
            { "uuidcolumn": "id", "strattr": "expenseId" },
            { "uuidcolumn": "parent_expense_id", "strattr": "parentExpenseId" },
            { "uuidcolumn": "category_id", "strattr": "categoryId" }
        ]
        super().__init__(typechangelist = typechanges,**kwargs)


class AccountResource(BaseResource):
    accountId: Optional[str] = Field(alias="id", default=None)
    accountNumber: Optional[str] = Field(alias="account_number", default=None)
    shortName: str = Field(alias="short_name")
    accountName: Optional[str] = Field(alias="account_name", default=None)
    typeId: Optional[str] = Field(alias="type_id", default=None)
    """this is in corelated to AccountType resource, the value must be accountTypeId"""
    tags: List[str] = []
    institutionName: Optional[str] = Field(alias="institution_name", default=None)
    description: Optional[str] = None

    def __init__(self, **kwargs):
        typechanges = [
            { "uuidcolumn": "id", "strattr": "accountId" },
            { "uuidcolumn": "type_id", "strattr": "typeId" }
        ]
        super().__init__(typechangelist = typechanges,**kwargs)


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
            { "uuidcolumn": "id", "strattr": "configId" }
        ]
        super().__init__(typechangelist = typechanges,**kwargs)


class ConfigTypeQueryModel(SerializeModel):
    belongsTo: Optional[str] = Field(alias="belongs_to", default=None)
    configId: Optional[str] = Field(alias="id", default=None)


class BaseFilterQueryModel(SerializeModel):
    name: Optional[str] = None
    fromDate: Optional[datetime] = None
    toDate: Optional[datetime] = None
    all: Optional[bool] = None
    pageNumber: Optional[int] = None
    pageSize: Optional[int] = None


class UserResource(BaseResource):
    userId: Optional[str] = Field(alias="id", default=None)
    username: str
    password: str
    encrypt_type: str
    email_id: Optional[str]
    phone_number: Optional[str]

    def __init__(self, **kwargs):
        typechanges = [ { "uuidcolumn": "id", "strattr": "userId" } ]
        super().__init__(typechangelist = typechanges,**kwargs)

