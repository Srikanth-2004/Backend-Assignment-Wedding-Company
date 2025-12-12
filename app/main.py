from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from app.database import db
from app.models import OrgCreateRequest, OrgResponse, AdminLoginRequest, TokenResponse, OrgUpdateRequest
from app.services import OrganizationService
from app.auth import AuthService

# Lifecycle event to connect/close DB
@asynccontextmanager
async def lifespan(app: FastAPI):
    db.connect()
    yield
    db.close()

app = FastAPI(lifespan=lifespan)
org_service = OrganizationService()

# Security Scheme
security = HTTPBearer()

# --- Security Dependency ---
async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  # Extract the token string
    payload = AuthService.decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

# --- Auth Endpoints ---
@app.post("/admin/login", response_model=TokenResponse)
async def login(creds: AdminLoginRequest):
    user = await db.get_master_db()["users"].find_one({"email": creds.email})
    if not user or not AuthService.verify_password(creds.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token with user email and org name
    token = AuthService.create_access_token({"sub": user["email"], "org": user["organization_name"]})
    return {"access_token": token, "token_type": "bearer"}

# --- Organization Endpoints ---

# Public: Anyone can create an org
@app.post("/org/create", response_model=OrgResponse)
async def create_org(request: OrgCreateRequest):
    return await org_service.create_organization(request)

# Public: Anyone can view (You can lock this too if you want)
@app.get("/org/get")
async def get_org(organization_name: str):
    return await org_service.get_organization(organization_name)

# PROTECTED: Only logged in admins can update
@app.put("/org/update", dependencies=[Depends(get_current_admin)])
async def update_org(organization_name: str = Body(...), 
                     new_data: OrgUpdateRequest = Body(...)):
    return await org_service.update_organization(organization_name, new_data)

# PROTECTED: Only logged in admins can delete
@app.delete("/org/delete", dependencies=[Depends(get_current_admin)])
async def delete_org(organization_name: str):
    return await org_service.delete_organization(organization_name)