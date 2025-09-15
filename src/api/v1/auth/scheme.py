from pydantic import BaseModel, model_validator, ConfigDict

# Request models
class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str

    @model_validator(mode='after')
    def validate_email(self):
        if not self.email or '@' not in self.email:
            raise ValueError('Invalid email address')
        return self

    @model_validator(mode='after')
    def validate_password(self):
        if len(self.password) < 8:
            raise ValueError('Password must be at least 8 characters')
        return self

    model_config = ConfigDict(extra="forbid")

class LoginRequest(BaseModel):
    email: str
    password: str

    @model_validator(mode='after')
    def validate_password(self):
        if len(self.password) < 8:
            raise ValueError('Password must be at least 8 characters')
        return self

# Response models
class AuthResponse(BaseModel):
    token: str
    user_id: int
    expires_in: int
