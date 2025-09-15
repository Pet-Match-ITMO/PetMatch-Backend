import os
import uvicorn
from quart import Quart
from quart_schema import QuartSchema
from src.api import api_bp
from src.db import DBHelper

app = Quart(__name__)
app.register_blueprint(api_bp)

@app.while_serving
async def lifespan():
    app.config['db_helper'] = DBHelper(os.environ['DB_URL'])
    yield

QuartSchema(app)


if __name__ == "__main__":
    uvicorn.run(app)
