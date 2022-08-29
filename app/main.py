import os
from web_api.app import create_app

if __name__ == "__main__":
    app = create_app(
        api_title=os.environ["API_TITLE"],
        api_version=os.environ["API_VERSION"],
        openapi_version=os.environ["OPENAPI_VERSION"],
    )
    app.run(host=os.environ["HOST"], port=int(os.environ["PORT"]))
