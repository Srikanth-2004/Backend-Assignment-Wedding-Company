from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Input Schemas
class OrgCreateRequest(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class OrgUpdateRequest(BaseModel):
    organization_name: str
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

# Response Schemas
class OrgResponse(BaseModel):
    organization_name: str
    collection_name: str
    admin_email: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str