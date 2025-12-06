###########################################################
# ITET Rapisardi da Vinci - Sostituzioni API (Unofficial) #
###########################################################

# Created by: @Matt0550 (GitHub)
# Dashboard routes

from fastapi import APIRouter, Form
from fastapi.requests import Request
from fastapi.responses import Response
from starlette.templating import Jinja2Templates

from core.db import Database
from core.logger_base import logger

router = APIRouter()
templates = Jinja2Templates("api/templates")

database = Database()


@router.get("/")
def dashboard_ui(request: Request, response: Response):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.post("/")
def dashboard_edit(request: Request, response: Response, email: str = Form(...), classe: str = Form(None), teacher: str = Form(None), delete: str = Form(None), telegram_chat_id: str = Form(None)):
    # Check if email in form
    if email is None or email == "":
        return templates.TemplateResponse("dashboard.html", {"request": request, "error": "Email not set"})

    # Check if email is valid
    if "@" not in email or "." not in email:
        return templates.TemplateResponse("dashboard.html", {"request": request, "error": "Invalid email"})

    # Check if email is already in the database
    user = database.get_user_by_email(email)
    if user is not None:
        # Update telegram chat id if provided
        if telegram_chat_id is not None:
            database.update_telegram_chat_id(email, telegram_chat_id)
            user = database.get_user_by_email(email) # Refresh user data

        if delete is not None and (delete == "true" or delete is True):
            if classe:
                logger.info("Deleting " + str(classe) + " from " + email)
                if database.delete_class_from_user(email, classe):
                    user = database.get_user_by_email(email)
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "success": "Class deleted"})
                else:
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "error": "Class not found"})
            elif teacher:
                logger.info("Deleting teacher " + str(teacher) + " from " + email)
                if database.delete_teacher_from_user(email, teacher):
                    user = database.get_user_by_email(email)
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "success": "Teacher deleted"})
                else:
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "error": "Teacher not found"})

        elif delete is not None and (delete == "false" or delete is False):
            if classe:
                logger.info("Adding " + str(classe) + " to " + email)
                if database.add_class_to_user(email, classe):
                    user = database.get_user_by_email(email)
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "success": "Class added"})
                else:
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "error": "Class not found"})
            elif teacher:
                logger.info("Adding teacher " + str(teacher) + " to " + email)
                if database.add_teacher_to_user(email, teacher):
                    user = database.get_user_by_email(email)
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "success": "Teacher added"})
                else:
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "error": "Error adding teacher"})
    
        else:
            return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

    return templates.TemplateResponse("dashboard.html", {"request": request, "error": "User not found"})
