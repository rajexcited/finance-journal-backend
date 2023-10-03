from flask import Flask
from flask_pydantic import validate
from flask_cors import cross_origin
from rest.expense_service import ExpenseResource, ExpenseService
from rest.account_service import AccountResource, AccountService
from rest.config_types_service import ConfigTypeResource, ConfigTypeService
from rest.resource import (
    UserResource,
    BaseFilterQueryModel,
    ConfigTypeQueryModel
)


app = Flask(__name__)
ROOT_PATH = "/my-finance/rest"

expense_service = ExpenseService()
account_service = AccountService()
config_type_service = ConfigTypeService()


@app.get(ROOT_PATH + "/expenses")
@cross_origin()
@validate(response_many=True)
def get_expenses(query: BaseFilterQueryModel):
    results = expense_service.get_expenses()
    app.logger.debug("result is received")
    return results


@app.post(ROOT_PATH + "/expenses")
@cross_origin()
@validate()
def add_update_expense(body: ExpenseResource):
    if body.expenseId:
        response = expense_service.update_expense(body)
        return response, 200
    else:
        response = expense_service.add_expense(body)
        return response, 201


@app.delete(ROOT_PATH + "/expenses/<expense_id>")
@cross_origin()
@validate()
def delete_expense(expense_id: str):
    response = expense_service.delete_expense(expense_id)
    return response, 200


@app.get(ROOT_PATH + "/accounts")
@cross_origin()
@validate(response_many=True)
def get_accounts(query: BaseFilterQueryModel):
    results = account_service.get_accounts()
    app.logger.debug("result is received")
    return results


@app.post(ROOT_PATH+"/accounts")
@cross_origin()
@validate()
def add_update_account(body: AccountResource):
    if body.accountId:
        account_service.update_account(body)
    else:
        account_service.add_account(body)


@app.get(ROOT_PATH + "/config/types")
@cross_origin()
@validate(response_many=True)
def get_config_types(query: ConfigTypeQueryModel):
    result = config_type_service.get_config_types(query)
    app.logger.debug("result config types received")
    return result


@app.post(ROOT_PATH + "/config/types")
@cross_origin()
@validate()
def add_update_config_type(body: ConfigTypeResource):
    if body.configId:
        updated = config_type_service.update_config_type(body)
        if not updated:
            return "cannot update config type. unable to find one.", 404
        return "successfully updated"
    else:
        id = config_type_service.add_config_type(body)
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
