import logging
from typing import Dict, Any
import psycopg2
from psycopg2.extensions import connection, cursor
from utils import config as util
from datetime import datetime
import sqlalchemy
from sqlalchemy.engine import URL
from utils import SerializeModel


class DBProperties(SerializeModel):
    user: str
    password: str
    database: str
    host: str
    created_on: str
    updated_on: str = datetime.now().ctime()
    created_by: str
    updated_by: str

def db_cursor(func):
    def with_connection_(*args, **kwargs):
        logger.debug("create connection")
        config:Dict[str, Any] = {
            "user":db_config.user, 
            "password": db_config.password, 
            "database":db_config.database, 
            "host": db_config.host
        }
        conn: connection = psycopg2.connect(**config)
        logger.debug("connection is created, now getting cursor")
        cur: cursor = conn.cursor()
        try:
            logger.debug("executing calling function")
            rv = func(cur, *args, **kwargs)
        except:
            conn.rollback()
            logger.error("db error. rollbacked the db changes if any")
            raise
        else:
            logger.debug("no error, so commit the db changes")
            conn.commit()
            return rv
        finally:
            logger.debug("closing cursor and db connection")
            cur.close()
            conn.close()
    return with_connection_

def create_engine():
    config: Dict[str, Any] = {
        "username": db_config.user,
        "password": db_config.password,
        "database": db_config.database,
        "host": db_config.host
    }
    url = URL.create(drivername="postgresql", **config)
    engine = sqlalchemy.create_engine(url, echo=True)
    return engine

def get_db_config(filename="props/database.ini", section="postgresql") -> DBProperties:
    logger.debug(f"reading section {section} from file, {filename}")
    config = util.get_config(filename, section)
    logger.debug(f"read config is {str(config)}")
    try:
        db_conf = DBProperties(**config)
    except:
        db_conf = DBProperties(**config, created_on=config['datetime'], created_by='neelsheth', updated_by='neelsheth')
        write_db_config(db_conf, section="postgresql2")

    return db_conf


def write_db_config(db_config: DBProperties, filename="props/database.ini", section="postgresql"):
    logger.info(f"writing config as section [{section}] in file {filename}")
    util.write_config(db_config.model_dump(), filename, section)
    logger.info("config is written")


@db_cursor
def version(cur):
    cur.execute("SELECT version()")
    db_version = cur.fetchone()
    logger.info(db_version)


logger = logging.getLogger(__name__)
db_config = get_db_config()

logger.debug("verifying db connection")
version() # type: ignore

alchemy_engine = create_engine()
