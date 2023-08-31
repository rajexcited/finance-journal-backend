from db.base import db_cursor, alchemy_engine
from sqlalchemy import MetaData, Text
from db.tables import ConfigTypes
from psycopg2.extensions import cursor


# later i have to be careful for table creation, probably need to rename or back existing table
# ConfigTypes.metadata.drop_all(alchemy_engine)
# ConfigTypes.metadata.create_all(alchemy_engine)


@db_cursor
def update_config_types(cur:cursor):
    create_status_column_sql = f"""\
    ALTER TABLE {ConfigTypes.__tablename__} ADD status TEXT;
    UPDATE {ConfigTypes.__tablename__} set status='active';
    ALTER TABLE {ConfigTypes.__tablename__} ALTER COLUMN status SET NOT NULL;
    """
    cur.execute(create_status_column_sql)


