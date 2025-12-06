###########################################################
# ITET Rapisardi da Vinci - Sostituzioni API (Unofficial) #
###########################################################

# Created by: @Matt0550 (GitHub)
# Dashboard routes

from fastapi import APIRouter, Form, HTTPException, BackgroundTasks
from fastapi.requests import Request
from fastapi.responses import Response
from starlette.templating import Jinja2Templates

from core.update_db import checkUpdates
from core.config import settings
from core.logger_base import logger

router = APIRouter()
templates = Jinja2Templates("api/templates")

# Exclude from docs
@router.post('/update_db', include_in_schema=False)
def update_db(request: Request, response: Response, background_tasks: BackgroundTasks, token: str = Form(...)):
    if token is not None:
        # Check if the request is from localhost
        if token == settings.ADMIN_TOKEN:
            client_host = request.client.host
            user_identifier = "Localhost" if client_host in ["::1", "127.0.0.1"] else client_host
            logger.info(f"Update triggered by {user_identifier}")
            
            # Check for updates in background
            background_tasks.add_task(checkUpdates)
            return "Update started in background"
        else:
            logger.warning(f"Unauthorized update attempt from {request.client.host}")
            raise HTTPException(status_code=401, detail="Unauthorized")
    else:
        raise HTTPException(status_code=400, detail="Token not provided")