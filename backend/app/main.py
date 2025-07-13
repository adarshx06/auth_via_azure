from fastapi import FastAPI, Depends
from app.authutils import AzureADAuthenticator

class EmployeeAPI:
    def __init__(self, app: FastAPI):
        self.app = app
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/health")
        async def health_check():
            return {"status": "ok"}

        @self.app.get("/employees")
        async def list_employees(user=Depends(authenticator.get_current_user())):
            return {
                "employees": [
                    {"name": "Alice", "role": "Engineer"},
                    {"name": "Bob", "role": "Manager"},
                    {"name": "Charlie", "role": "Analyst"}
                ],
                "user_claims": user
            }

# Replace with your Azure AD values
TENANT_ID = "46c69e96-00e5-4617-a008-14ad420d9c56"
CLIENT_ID = "2d830ac7-1a1e-4a51-a5f9-04fb25ba4c19"

app = FastAPI()

authenticator = AzureADAuthenticator(TENANT_ID, CLIENT_ID)

# Initialize routes
EmployeeAPI(app)
