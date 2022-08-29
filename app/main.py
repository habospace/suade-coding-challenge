import os

from pandas import read_csv

from web_api.app import create_app

if __name__ == "__main__":
    app = create_app(
        api_title=os.environ["API_TITLE"],
        api_version=os.environ["API_VERSION"],
        openapi_version=os.environ["OPENAPI_VERSION"],
        orders=read_csv(os.environ["ORDERS_FILE_PATH"]),
        order_lines=read_csv(os.environ["ORDERS_LINES_FILE_PATH"]),
        commissions=read_csv(os.environ["COMMISSIONS_FILE_PATH"]),
        product_promotions=read_csv(os.environ["PRODUCT_PROMOTIONS_FILE_PATH"]),
        products=read_csv(os.environ["PRODUCTS"]),
        promotions=read_csv(os.environ["PROMOTIONS"])
    )
    app.run(host=os.environ["HOST"], port=int(os.environ["PORT"]))
