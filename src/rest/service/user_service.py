from typing import Optional, Union
import logging
from uuid import UUID
from pydantic import Field
from utils import SerializeModel
from db.base import alchemy_engine
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from rest.resource import BaseResource, UUID_VALIDATE_PATTERN
from db.tables import UserTable as DBUser
from enum import Enum
import base64

logger = logging.getLogger(__name__)


class UserStatus(Enum):
    # onhold, suspicious, investigation, transferred,
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class UserResource(BaseResource):
    """A rest resource with validations. this resource is converted to/from Database. 
    """
    user_id: Optional[str] = Field(alias="id", default=None, pattern=UUID_VALIDATE_PATTERN,
                                   max_length=32, description="uuid created and used by db, unrelevant to UI")
    username: Optional[str] = Field(
        default=None, pattern=r'^\w+$', max_length=25, description="username for login purpose")
    password: Optional[str] = Field(
        default=None, pattern=r'^(?=.*[\d])(?=.*[A-Z])(?=.*[!@#$%^&*])[\w!@#$%^&\(\)\=*]{8,25}$', max_length=25, min_length=8, description="for login purpose. it's reversed value. eg hello -> olleh")
    new_password: Optional[str] = Field(alias="newPassword",
                                        default=None, pattern=r'^(?=.*[\d])(?=.*[A-Z])(?=.*[!@#$%^&*])[\w!@#$%^&\(\)\=*]{8,25}$', max_length=25, min_length=8, description="to update existing password. it's reversed value. eg hello -> olleh")
    email_id: Optional[str] = Field(
        alias="emailId", default=None, pattern=r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', max_length=50, description="primary email id, can be used to login as alternative to username")
    phone_number: Optional[str] = Field(
        alias="phoneNo", default=None, pattern=r'^+\d{1,3}-\d{10}$', max_length=15, description="primary phone no.")
    first_name: Optional[str] = Field(
        alias="firstName", default=None, pattern=r'[\w\s]+', max_length=25, description="first name")
    last_name: Optional[str] = Field(
        alias="lastName", default=None, pattern=r'[\w\s]+', max_length=25, description="last name")
    expires_in: Optional[int] = Field(alias="expiresIn", default=None, ge=0,
                                      description="expiring seconds. uses to indicate when session will expire")
    access_token: Optional[str] = Field(alias="accessToken", default=None, max_length=40,
                                        description="session token to allow access to protected service")
    status: UserStatus = Field(
        default=UserStatus.ACTIVE, description="current user status to help manage user")
    notes: Optional[str] = Field(
        default=None, description="json schema notes with atleast these props - type, note")

    def __init__(self, **kwargs):
        typechanges = [{"uuidcolumn": "id", "strattr": "user_id"}]
        super().__init__(typechangelist=typechanges, **kwargs)


class UserService(SerializeModel):
    """A Rest Service to support Rest API functionalities. 
    Allows to add user, get user, update user
    """

    def add_user(self, user: UserResource) -> UserResource:
        """ validates user details and adds user to Database.
                Parameters:
                    user: user details to be created
                Returns:
                    created user detail
        """
        try:
            logger.debug("entering add_user method")
            assert user.email_id, "email id must be provided"
            assert user.password, "password must be provided"
            assert user.first_name, "first name must be provided"
            assert user.last_name, "last name must be provided"
            new_user = UserResource(
                *user,
                status=UserStatus.ACTIVE,
                password=self.encode_password(user.password)
            )
            del new_user.user_id

            with Session(alchemy_engine) as session:
                stmt = select(DBUser).filter_by(email_id=new_user.email_id)
                found_db_user = session.scalar(stmt)
                if found_db_user:
                    raise ValueError("email id exists")
                db_user = DBUser.from_model(new_user)
                session.add(db_user)
                session.commit()
                logger.info("new user has been created in DB: " +
                            str(db_user.id))
                returning_user = self.get_user(db_user.id, session)
            if returning_user:
                return returning_user
        except Exception as e:
            logger.error("unable to add user", exc_info=True)
            raise ValueError("unable to add user")
        finally:
            logger.debug("exiting add_user method")
        raise ValueError(
            "this should never be executed, since entry has just been added")

    def update_user(self, user: UserResource) -> UserResource:
        """ Updates user details
                Parameters:
                    user: user details
                Returns:
                    updated user details
        """
        logger.debug("entering update_user method")
        assert user.user_id, "user id must be provided"
        with Session(alchemy_engine) as session:
            stmt = select(DBUser).filter_by(id=user.user_id)
            found_db_user = session.scalar(stmt)
            if not found_db_user:
                logger.error("user is not found")
                raise ValueError("user does not exist")
            db_user = DBUser.from_model(user)
            found_db_user.update_entry(db_user)
            session.commit()
            returning_user = self.get_user(user.user_id, session)
        logger.debug("exiting update_user method")
        if returning_user:
            return returning_user
        raise ValueError(
            "this should never be executed, since entry has just been updated")

    def get_user(self, user_id: Union[str, UUID], session: Session) -> Optional[UserResource]:
        """ retrieves an user detail
            Parameters:
                user_id: uuid of user
                session: alchemy session
            Returns:
                user details from DB
        """
        logger.debug("entering get_user method")
        logger.debug("user_id: " + str(type(user_id)))
        if not user_id:
            raise ValueError("incorrect user id")
        if isinstance(user_id, UUID):
            id = user_id
        else:
            id = UUID(user_id)
        db_user = session.query(DBUser).filter_by(id=id).first()
        try:
            if db_user:
                returning_user = UserResource.from_db_entry(db_user)
                return returning_user
            return None
        finally:
            logger.debug("exiting get_user method")

    def delete_user(self, user: UserResource) -> None:
        """ updates the status of user to deleted
        """
        logger.debug("entering delete_user method")
        try:
            if self.is_user_validated(user):
                self.update_user(UserResource(
                    user_id=user.user_id, status=UserStatus.DELETED))
            else:
                raise ValueError("invalid user")
        finally:
            logger.debug("exiting delete_user method")

    def is_user_validated(self, user: UserResource) -> bool:
        """ validates userId, username/emailId, password
                Parameters:
                    user: user details
                Returns:
                    true if matches all info
                    false otherwise
        """
        logger.debug("entering delete_user method")
        try:
            assert user.user_id, "user id must be provided"
            assert user.email_id, "email id must be provided"
            assert user.password, "password must be provided"

            with Session(alchemy_engine) as session:
                found_user = self.get_user(user.user_id, session)
                if found_user:
                    if found_user.email_id == user.email_id:
                        if found_user.password:
                            current_password = self.encode_password(
                                found_user.password)
                            return current_password == found_user.password
            return False
        finally:
            logger.debug("exiting delete_user method")

    def encode_password(self, password: str) -> str:
        """ encodes password """
        logger.debug("entering encode_password method")
        encoded_ascii_bytes = password.encode("ascii")
        encoded_b64_bytes = base64.b64encode(encoded_ascii_bytes)
        decoded_str = encoded_b64_bytes.decode("ascii")
        logger.debug("exiting encode_password method")
        return decoded_str

    def decode_password(self, password: str) -> str:
        """ decodes password """
        logger.debug("entering decode_password method")
        encoded_ascii_bytes = password.encode("ascii")
        decoded_b64_bytes = base64.b64decode(encoded_ascii_bytes)
        decoded_str = decoded_b64_bytes.decode("ascii")
        logger.debug("exiting decode_password method")
        return decoded_str
