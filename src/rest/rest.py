from flask import Flask, jsonify
from flask_pydantic import validate
from flask_cors import cross_origin
from rest.resource import (
    ExpenseResource, 
    AccountResource, 
    UserResource, 
    ConfigTypeResource,
    BaseFilterQueryModel, 
    ConfigTypeQueryModel
)
from rest import service


app = Flask(__name__)
ROOT_PATH = "/my-finance/rest"

@app.get(ROOT_PATH + "/expenses")
@cross_origin()
@validate(response_many=True)
def get_expenses(query: BaseFilterQueryModel):
    # priority 1
    results = service.get_expenses()
    app.logger.debug("result is received")
    app.logger.debug(results)
    return results


@app.post(ROOT_PATH + "/expenses")
@cross_origin()
@validate()
def add_update_expense(body: ExpenseResource):
    # priority 1
    service.add_expense(body)
    return "created", 201


@app.get(ROOT_PATH + "/accounts")
@validate()
def get_accounts(query: BaseFilterQueryModel):
    # priority 1
    pass


@app.post(ROOT_PATH+"/accounts")
@validate()
def add_update_account(body: AccountResource):
    # priority 1
    pass


@app.get(ROOT_PATH + "/config/types")
@cross_origin()
@validate(response_many=True)
def get_config_types(query: ConfigTypeQueryModel):
    return service.get_config_types(query)


@app.post(ROOT_PATH + "/config/types")
@cross_origin()
@validate()
def add_update_config_type(body: ConfigTypeResource):
    if body.configId:
        updated = service.update_config_type(body)
        if not updated:
            return "cannot update config type. unable to find one.", 404
        return "successfully updated"
    else:
        id = service.add_config_type(body)
        return id


@app.get(ROOT_PATH+"/settings")
def get_settings():
    # lesser priority - at the end of finalize app, when creating shareable profile,
    # user preferences for view config, and some other configurations
    pass


@app.post(ROOT_PATH + "/login")
@validate()
def authenticate(body: UserResource):
    # lesser priorty - at the end of finalize app, when create a sharable profile
    pass


@app.post(ROOT_PATH + "/signup")
def first_time_setup():
    # lesser priority, needed when I will be to ready to pass it to Guddu
    pass
