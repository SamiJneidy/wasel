from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError
from .exceptions import BaseAppException
from src.zatca.exceptions import BaseZatcaException


# from app.core.exceptions.database_exceptions import ForeignKeyViolationException, UniqueConstraintViolationException

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(BaseAppException)
    async def base_exception_handler(request: Request, exc: BaseAppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail
            }
        )

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
            },
        )
    
    @app.exception_handler(BaseZatcaException)
    async def zatca_exception(request: Request, exc: BaseZatcaException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "zatca_response": exc.zatca_response
            },
        )
    
    # @app.exception_handler(ForeignKeyViolationException)
    # async def fk_exception_handler(request: Request, exc: ForeignKeyViolationException):
    #     return JSONResponse(
    #         status_code=400,
    #         content={
    #             "statusCode": 400,
    #             "detail": exc.detail,
    #         },
    #     )
    
    # @app.exception_handler(UniqueConstraintViolationException)
    # async def unique_exception_handler(request: Request, exc: UniqueConstraintViolationException):
    #     return JSONResponse(
    #         status_code=409,
    #         content={
    #             "statusCode": 409,
    #             "detail": exc.detail,
    #         },
    #     )
    