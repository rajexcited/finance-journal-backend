import utils.log_setup
from rest import rest

# first time - create tables
# import db.create_tables
# from db.table_create_update import update_config_types
# update_config_types() # type: ignore


# start flask app - rest app
rest.app.run(debug=False)
