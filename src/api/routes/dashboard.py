###########################################################
# ITET Rapisardi da Vinci - Sostituzioni API (Unofficial) #
###########################################################

# Created by: @Matt0550 (GitHub)
# Dashboard routes

from fastapi import APIRouter, Form
from fastapi.requests import Request
from fastapi.responses import Response
from starlette.templating import Jinja2Templates
from pathlib import Path

from core.db import Database
from core.logger_base import logger

router = APIRouter()
# Get the absolute path to the templates directory
# Current file: src/api/routes/dashboard.py
# Templates: src/api/templates
templates_dir = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

database = Database()


@router.get("/")
def dashboard_ui(request: Request, response: Response):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.post("/")
def dashboard_edit(request: Request, response: Response, email: str = Form(...), classe: str = Form(None), teacher: str = Form(None), delete: str = Form(None), telegram_chat_id: str = Form(None), fuzzy_teacher_matching: str = Form(None), update_settings: str = Form(None), sede: str = Form("margherita"), action: str = Form(None)):
    # Check if email in form
    if email is None or email == "":
        return templates.TemplateResponse("dashboard.html", {"request": request, "error": "Email not set"})

    # Check if email is valid
    if "@" not in email or "." not in email:
        return templates.TemplateResponse("dashboard.html", {"request": request, "error": "Invalid email"})

    # Handle registration
    if action == "register":
        if database.get_user_by_email(email):
             return templates.TemplateResponse("dashboard.html", {"request": request, "error": "Utente già registrato"})
        database.insert_user(email, [])
        user = database.get_user_by_email(email)
        return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "success": "Registrazione completata"})

    # Check if email is already in the database
    user = database.get_user_by_email(email)
    
    # Handle profile deletion
    if action == "delete_profile":
        if user:
            database.delete_user(email)
            return templates.TemplateResponse("dashboard.html", {"request": request, "success": "Profilo eliminato correttamente"})
        else:
             return templates.TemplateResponse("dashboard.html", {"request": request, "error": "Utente non trovato"})

    if user is not None:
        # Update settings if requested
        if update_settings == "true":
            if telegram_chat_id is not None:
                database.update_telegram_chat_id(email, telegram_chat_id)
            
            # Handle fuzzy matching checkbox
            # If checkbox is checked, fuzzy_teacher_matching will be "on" (or whatever value), if not, it will be None
            is_fuzzy = fuzzy_teacher_matching is not None
            database.update_fuzzy_matching(email, is_fuzzy)
            
            user = database.get_user_by_email(email) # Refresh user data
            return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "success": "Settings updated"})

        if delete is not None and (delete == "true" or delete is True):
            if classe:
                logger.info("Deleting " + str(classe) + " (" + sede + ") from " + email)
                if database.delete_class_from_user(email, classe, sede):
                    user = database.get_user_by_email(email)
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "success": "Class deleted"})
                else:
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "error": "Class not found"})
            elif teacher:
                logger.info("Deleting teacher " + str(teacher) + " (" + sede + ") from " + email)
                if database.delete_teacher_from_user(email, teacher, sede):
                    user = database.get_user_by_email(email)
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "success": "Teacher deleted"})
                else:
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "error": "Teacher not found"})

        elif delete is not None and (delete == "false" or delete is False):
            if classe:
                logger.info("Adding " + str(classe) + " (" + sede + ") to " + email)
                if database.add_class_to_user(email, classe, sede):
                    user = database.get_user_by_email(email)
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "success": "Class added"})
                else:
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "error": "Class not found"})
            elif teacher:
                logger.info("Adding teacher " + str(teacher) + " (" + sede + ") to " + email)
                if database.add_teacher_to_user(email, teacher, sede):
                    user = database.get_user_by_email(email)
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "success": "Teacher added"})
                else:
                    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "error": "Error adding teacher"})
    
        else:
            return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

    return templates.TemplateResponse("dashboard.html", {"request": request, "error": "User not found"})
