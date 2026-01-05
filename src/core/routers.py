from fastapi import APIRouter
from src.auth.routers import router as auth_router
from src.users.routers import router as users_router
from src.customers.routers import router as customers_router
from src.organizations.routers import router as organizations_router
from src.branches.routers import router as branches_router
from src.suppliers.routers import router as suppliers_router
from src.items.routers import router as items_router
from src.buy_invoices.routers import router as buy_invoices_router
from src.sale_invoices.routers import router as sale_invoices_router
v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(auth_router)
v1_router.include_router(users_router)
v1_router.include_router(organizations_router)
v1_router.include_router(branches_router)
v1_router.include_router(customers_router)
v1_router.include_router(suppliers_router)
v1_router.include_router(items_router)
v1_router.include_router(buy_invoices_router)
v1_router.include_router(sale_invoices_router)