from datetime import datetime
import uvicorn
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from typing import Any

from core.config import settings
from core.logger_base import logger
from api.routes import sostituzioni, orario, dashboard, admin

from pydantic import BaseModel
load_dotenv()

start_time = datetime.now() # For the uptime

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

class CustomResponse(JSONResponse):
    def __init__(self, content: Any, status_code: int = 200, *args, **kwargs):
        # Customize content and pass my new content...
        content = ResponseStructure(
            details=content, success=False if status_code != 200 else True, status_code=status_code
        )
        super().__init__(*args, content=content.dict(), status_code=status_code, **kwargs)


class ResponseStructure(BaseModel):
    details: Any
    success: bool = True
    status_code: int


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    generate_unique_id_function=custom_generate_unique_id,
    default_response_class=CustomResponse,
    version=settings.API_VERSION,
)


cors_origins = settings.BACKEND_CORS_ORIGINS if settings.BACKEND_CORS_ORIGINS else []

# Se non ci sono origins configurati, usa dei default per development
if not cors_origins or len(cors_origins) == 0:
    cors_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5500",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Permette le origini specificate
    allow_credentials=True,  # Permette cookies/auth headers
    allow_methods=["*"],  # Permette tutti i metodi HTTP
    allow_headers=["*"],  # Permette tutti gli headers
    expose_headers=["*"],  # Espone tutti gli headers nella risposta
)

if (settings.ENABLE_RATE_LIMITING):
    limiter = Limiter(
        key_func=get_remote_address,
        application_limits=["100 per hour", "20 per minute", "5 per 10 seconds"],
        enabled=settings.ENABLE_RATE_LIMITING,
    )
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(Exception)
async def validation_exception_handler1(_request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        content={
            "details": "Internal server error. Please try again later.",
            "status": "error",
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@app.exception_handler(StarletteHTTPException)
async def my_custom_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            content={"details": "Not found", "status": "error", "code": exc.status_code},
            status_code=exc.status_code,
        )
    if exc.status_code == 405:
        return JSONResponse(
            content={"details": "Method not allowed", "status": "error", "code": exc.status_code},
            status_code=exc.status_code,
        )
    # Just use FastAPI's built-in handler for other errors
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler2(_request: Request, exc: RequestValidationError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    logger.error(f"Validation error: {exc.errors()}")

    if exc.errors()[0]["type"] == "value_error.any_str.max_length":
        limit = str(exc.errors()[0]["ctx"]["limit_value"])
        return JSONResponse(
            content={
                "details": "The value entered is too long. Max length is " + limit,
                "status": "error",
                "code": status_code,
            },
            status_code=status_code,
        )
    if exc.errors()[0]["type"] == "value_error.missing" or exc.errors()[0]["type"] == "missing":
        missing = []
        for error in exc.errors():
            # Costruisci il percorso completo del campo come stringa
            if error["loc"]:
                field_path = ".".join(str(loc) for loc in error["loc"])
                if field_path not in missing:
                    missing.append(field_path)
            else:
                if "unknown field" not in missing:
                    missing.append("unknown field")

        missing_fields = ", ".join(missing)
        return JSONResponse(
            content={
                "details": f"Required fields missing: {missing_fields}",
                "status": "error",
                "code": status_code,
            },
            status_code=status_code,
        )
    return JSONResponse(
        content={"details": exc.errors()[0]["msg"], "status": "error", "code": status_code},
        status_code=status_code,
    )


@app.exception_handler(ResponseValidationError)
async def validation_exception_handler3(_request: Request, exc: RequestValidationError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    logger.error(f"Validation error: {exc.errors()}")

    if exc.errors()[0]["type"] == "value_error.any_str.max_length":
        limit = str(exc.errors()[0]["ctx"]["limit_value"])
        return JSONResponse(
            content={
                "details": "The value entered is too long. Max length is " + limit,
                "status": "error",
                "code": status_code,
            },
            status_code=status_code,
        )
    if exc.errors()[0]["type"] == "value_error.missing":
        missing = []
        for error in exc.errors():
            try:
                missing.append(error["loc"][1])
            except Exception:
                missing.append(error["loc"][0])

        return JSONResponse(
            content={
                "details": "One or more fields are missing: " + str(missing),
                "status": "error",
                "code": status_code,
            },
            status_code=status_code,
        )
    return JSONResponse(
        content={"details": exc.errors()[0]["msg"], "status": "error", "code": status_code},
        status_code=status_code,
    )

@app.exception_handler(HTTPException)
async def validation_exception_handler4(_request: Request, exc: HTTPException):
    logger.error(f"HTTP error: {exc.detail}")

    return JSONResponse(
        content={"details": exc.detail, "status": "error", "code": exc.status_code},
        status_code=exc.status_code,
    )

api_router = APIRouter()

@api_router.get("/", tags=["root"])
def home() -> dict:
    """
    Root endpoint.
    """
    return "Welcome to Rapisardi Notifications API! If you want to see the documentation, go to /docs or /redoc"


@api_router.get("/status", tags=["root"])
def status_health() -> dict:
    """
    Status endpoint.
    """
    uptime = datetime.now() - start_time
    return {"status": "ok", "version": settings.API_VERSION, "project": settings.PROJECT_NAME, "uptime": str(uptime)}


api_router.include_router(sostituzioni.router, prefix="/sostituzioni", tags=["sostituzioni"])
api_router.include_router(orario.router, prefix="/orario", tags=["orario"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    print(f"Rapisardi Notifications API v{settings.API_VERSION}")
    print("© @Matt0550. All rights reserved.")
    print("Running on port: ", settings.PORT)
    print("\nBuona fortuna.")
    print("100% Made in \033[1;32mIt\033[1;37mal\033[1;31my\033[0m")
    print("--------------------------------------------------")

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=False,
        log_level="info",
    )
