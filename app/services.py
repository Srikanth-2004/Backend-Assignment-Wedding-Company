from fastapi import HTTPException, status
from app.database import db
from app.auth import AuthService
from app.models import OrgCreateRequest, OrgUpdateRequest

class OrganizationService:
    # Removed __init__ to prevent early DB access
    
    async def create_organization(self, data: OrgCreateRequest):
        # Get DB references dynamically inside the function
        master_orgs = db.get_master_db()["organizations"]
        master_users = db.get_master_db()["users"]

        # 1. Validate Organization Name Uniqueness
        existing_org = await master_orgs.find_one({"organization_name": data.organization_name})
        if existing_org:
            raise HTTPException(status_code=400, detail="Organization already exists")

        # 2. Create Dynamic Collection Name
        collection_name = f"org_{data.organization_name.lower().replace(' ', '_')}"
        
        # 3. Create Admin User
        hashed_password = AuthService.get_password_hash(data.password)
        admin_user = {
            "email": str(data.email),  # <--- FIXED: Converted to string
            "password": hashed_password,
            "role": "admin",
            "organization_name": data.organization_name
        }
        await master_users.insert_one(admin_user)

        # 4. Initialize the Dynamic Collection
        tenant_col = db.get_tenant_collection(collection_name)
        await tenant_col.insert_one({"type": "metadata", "created_at": "now"})

        # 5. Store Metadata in Master DB
        org_doc = {
            "organization_name": data.organization_name,
            "collection_name": collection_name,
            "admin_email": str(data.email) # <--- FIXED: Converted to string
        }
        await master_orgs.insert_one(org_doc)

        return org_doc

    async def get_organization(self, org_name: str):
        master_orgs = db.get_master_db()["organizations"]
        org = await master_orgs.find_one({"organization_name": org_name})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        return org

    async def update_organization(self, old_name: str, data: OrgUpdateRequest):
        master_orgs = db.get_master_db()["organizations"]
        master_users = db.get_master_db()["users"]
        
        # 1. Find existing org
        existing = await self.get_organization(old_name)
        
        # 2. Check if new name is taken (if name is changing)
        if data.organization_name != old_name:
            conflict = await master_orgs.find_one({"organization_name": data.organization_name})
            if conflict:
                raise HTTPException(status_code=400, detail="New organization name already exists")
            
            # 3. Dynamic Collection Migration (Rename)
            old_col_name = existing["collection_name"]
            new_col_name = f"org_{data.organization_name.lower().replace(' ', '_')}"
            
            try:
                await db.get_master_db().command(
                    "renameCollection", 
                    f"{db.settings.MASTER_DB_NAME}.{old_col_name}", 
                    to=f"{db.settings.MASTER_DB_NAME}.{new_col_name}"
                )
            except Exception as e:
                print(f"Migration note: {e}")

            # Update Metadata
            await master_orgs.update_one(
                {"organization_name": old_name},
                {"$set": {"organization_name": data.organization_name, "collection_name": new_col_name}}
            )

        # 4. Update Admin credentials if provided
        if data.email or data.password:
            update_fields = {}
            if data.email: update_fields["email"] = data.email
            if data.password: update_fields["password"] = AuthService.get_password_hash(data.password)
            
            await master_users.update_one(
                {"organization_name": old_name},
                {"$set": update_fields}
            )
            
        return {"status": "updated", "new_name": data.organization_name}

    async def delete_organization(self, org_name: str):
        master_orgs = db.get_master_db()["organizations"]
        master_users = db.get_master_db()["users"]

        org = await self.get_organization(org_name)
        
        # 1. Drop the dynamic collection
        col_name = org["collection_name"]
        await db.get_tenant_collection(col_name).drop()
        
        # 2. Remove metadata and users
        await master_orgs.delete_one({"organization_name": org_name})
        await master_users.delete_many({"organization_name": org_name})
        
        return {"status": "deleted"}