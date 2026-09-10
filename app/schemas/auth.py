from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    passcode: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str