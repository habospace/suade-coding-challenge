from flask import Flask
from flask_smorest import Api
from pandas import DataFrame

from web_api.views import api_blp
from data_repositories import DailyOrderSummaryRepository


def create_app(
        api_title: str, api_version: str, openapi_version: str,
        orders: DataFrame, order_lines: DataFrame,
        commissions: DataFrame, product_promotions: DataFrame,
        products: DataFrame, promotions: DataFrame
) -> Flask:
    app = Flask(__name__)
    app.config["API_TITLE"] = api_title
    app.config["API_VERSION"] = api_version
    app.config["OPENAPI_VERSION"] = openapi_version
    app.config["DAILY_ORDER_SUMMARY_REPOSITORY"] = DailyOrderSummaryRepository(
        orders=orders,
        order_lines=order_lines,
        commissions=commissions,
        product_promotions=product_promotions,
        products=products,
        promotions=promotions
    )
    api = Api(app)
    api.register_blueprint(api_blp)
    return app
