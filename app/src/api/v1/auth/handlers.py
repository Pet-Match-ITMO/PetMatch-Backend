import os
import datetime
import jwt
import dotenv
from quart import Blueprint, jsonify, current_app, abort
from quart_schema import validate_request, validate_response
from . import crud
from .scheme import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
)
from .exceptions import DatabaseException

dotenv.load_dotenv()

# Auth blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Registration route
@auth_bp.post("/register")
@validate_request(RegisterRequest)
@validate_response(AuthResponse, 200)
async def register(data: RegisterRequest):
    db_helper = current_app.config['db_helper']
    async with db_helper.make_session() as session:
        # Create user with secure password hashing
        try:
            if await crud.get_user_by_email(session, data.email) is not None:
                return abort(400, description="User already exists")

            new_user = await crud.create_user(session, data)
        except DatabaseException as e:
            return jsonify({"error": "User creation failed", "details": str(e)}), 500

        # Generate token
        secret_key = os.environ["JWT_SECRET"]
        token_data = {
            "user_id": new_user.id,
            "exp": datetime.datetime.now() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(token_data, secret_key, algorithm="HS256")
        
        return AuthResponse(token=token, user_id=new_user.id, expires_in=86400)


# Login route
@auth_bp.route("/login", methods=["POST"])
@validate_request(LoginRequest)
@validate_response(AuthResponse, 200)
async def login(data: LoginRequest):
    db_helper = current_app.config['db_helper']
    async with db_helper.make_session() as session:
        # Authenticate user with password verification
        try:
            user = await crud.authenticate_user(session, data)
        except DatabaseException as e:
            return jsonify({"error": "Authentication failed", "details": str(e)}), 500
            
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        # Generate token
        secret_key = os.environ["JWT_SECRET"]
        token_data = {
            "user_id": user.id,
            "exp": datetime.datetime.now() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(token_data, secret_key, algorithm="HS256")
        
        return AuthResponse(token=token, user_id=user.id, expires_in=86400)