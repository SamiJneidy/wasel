import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.exceptions.exception_handlers import register_exception_handlers
from src.core.routers import v1_router

app = FastAPI(
    title="Wasel - Backend API",
    description="""
This is the **backend of Wasel**, a ZATCA Phase 2 compliant invoicing service.  
Here you can find the available **APIs**, their documentation, and how to integrate with Wasel in your applications.

---

### About Wasel
Wasel is a secure and user-friendly invoicing service designed to help businesses generate and manage electronic invoices while staying compliant with ZATCA requirements.

### Key Features
- 🔒 **Strong Authentication & Security**  
  User data, private keys, and certificates are stored securely using industry best practices to protect sensitive information.

- 📦 **Items & Customers Management**  
  Dedicated endpoints to manage items and customers, making invoice creation seamless.

- 🧾 **ZATCA-Compliant Invoices**  
  Invoices are generated in the proper XML format with embedded QR codes, ensuring compatibility with ZATCA compliance standards.

- ⚡ **Automatic Certificate Handling**  
  Certificates required by ZATCA are generated and managed automatically by the system.

- 🛠 **Two-Stage Workflow**
  - **Compliance Stage**: Validate invoices with ZATCA before going live.  
  - **Production Stage**: Transition to live invoicing once compliance is approved.

- 👤 **Easy Sign-up & Integration**  
  Users can quickly sign up, link their accounts with ZATCA, and start issuing invoices.

---

Wasel Backend API makes **integration simple, secure, and reliable**. Use the docs below to explore endpoints, test requests, and integrate Wasel into your business workflows.
    """,
    version="1.0.0",
    contact={
        "name": "Wasel Support",
        "email": "support@wasel.com",
        "url": "https://wasel.com",
    },
)
# app = FastAPI(
#     swagger_ui_parameters={
#         "syntaxHighlight": False,   # disable purple highlighting for code blocks
#     }
# )
app.include_router(v1_router)

register_exception_handlers(app)

# Configure CORS
origins = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
    "http://localhost:3000",
    "https://wasel-black.vercel.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("server.app.main:app", host="0.0.0.0", port=8000, reload=True)