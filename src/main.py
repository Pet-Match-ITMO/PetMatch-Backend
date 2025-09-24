import os
import uvicorn

from quart import Quart
from quart_schema import QuartSchema
from werkzeug.exceptions import HTTPException

from src.api import api_bp
from src.db import DBHelper
from src.scheme import ErrorResponse

app = Quart(__name__)

QuartSchema(app)

app.register_blueprint(api_bp)

@app.while_serving
async def lifespan():
    app.config['db_helper'] = DBHelper(os.environ['DB_URL'])
    yield


@app.errorhandler(HTTPException)
async def handle_http_exception(e: HTTPException):
    # serialize HTTPException to JSON using a Pydantic model
    return ErrorResponse(error=e.name, detail=e.description).model_dump(), e.code


if __name__ == "__main__":
    uvicorn.run(app)
