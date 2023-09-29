###########################################################
# ITET Rapisardi da Vinci - Sostituzioni API (Unofficial) #
###########################################################

# Created by: @Matt0550 (GitHub)

# FastAPI
import datetime
import os
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import FastAPI, Request, Response, status, Form, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import uvicorn
from sostituzioni import Sostituzioni
from orario import Orario
from db import Database
from threading import Thread
# Init 
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

limiter = Limiter(key_func=get_remote_address, default_limits=["3/5seconds", "10/minute"])

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = ["http://127.0.0.1/", "http://localhost", "http://192.168.1.75", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SlowAPIMiddleware)

DATABASE = Database()
ALLOWED_ADMIN_IPS = [
    "localhost",
    "127.0.0.1",
    "192.168.1.75",
    "0.0.0.0"
]

# Handle the 404 error. Use HTTP_exception_handler to handle the error
@app.exception_handler(StarletteHTTPException)
async def my_custom_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(content={"message": "Not found", "status": "error", "code": exc.status_code}, status_code=exc.status_code)
    elif exc.status_code == 405:
        return JSONResponse(content={"message": "Method not allowed", "status": "error", "code": exc.status_code}, status_code=exc.status_code)
    else:
        # Just use FastAPI's built-in handler for other errors
        return await http_exception_handler(request, exc)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    print(exc.errors())

    if exc.errors()[0]["type"] == "value_error.any_str.max_length":
        limit = str(exc.errors()[0]["ctx"]["limit_value"])
        return JSONResponse(content={"message": "The value entered is too long. Max length is " + limit, "status": "error", "code": status_code}, status_code=status_code)
    elif exc.errors()[0]["type"] == "value_error.missing":
        missing = []
        for error in exc.errors():
            try:
                missing.append(error["loc"][1])
            except:
                missing.append(error["loc"][0])

        return JSONResponse(content={"message": "One or more fields are missing: " + str(missing), "status": "error", "code": status_code}, status_code=status_code)
    else:
        return JSONResponse(content={"message": exc.errors()[0]["msg"], "status": "error", "code": status_code}, status_code=status_code)
    
# @app.exception_handler(RateLimitExceeded)
# async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
#     return JSONResponse(content={"message": "Rate limit exceeded. Try again in " + str(exc.retry_after) + " seconds", "status": "error", "code": 429}, status_code=429)

# Routes margherita
@app.get("/sostituzioni/margherita/today/{classe}", tags=["Sostituzioni"])
@limiter.limit("1/second")
def sostituzioni_margherita_today(request: Request, response: Response, classe: str):
    # Check if the class is valid
    if classe != None:
        sostituzioni = Sostituzioni("https://www.rapisardidavinci.edu.it/sost/app/sostituzioni.php")
        updates = sostituzioni.getTodayUpdatesFromClass(classe)
        if updates != "null" and updates != None:
            return JSONResponse(content={"message": updates, "status": "success", "code": 200}, status_code=200)
        else:
            return JSONResponse(content={"message": "No updates", "status": "error", "code": 404}, status_code=404)

    return JSONResponse(content={"message": "Invalid class", "status": "error", "code": 400}, status_code=400)

@app.get("/sostituzioni/margherita/next/{classe}", tags=["Sostituzioni"])
@limiter.limit("1/second")
def sostituzioni_margherita_next(request: Request, response: Response, classe: str):
    # Check if the class is valid
    if classe != None:
        sostituzioni = Sostituzioni("https://www.rapisardidavinci.edu.it/sost/app/sostituzioni.php")
        updates = sostituzioni.getNextUpdatesFromClass(classe)
        if updates != "null" and updates != None:
            return JSONResponse(content={"message": updates, "status": "success", "code": 200}, status_code=200)
        else:
            return JSONResponse(content={"message": "No updates", "status": "error", "code": 404}, status_code=404)

    return JSONResponse(content={"message": "Invalid class", "status": "error", "code": 400}, status_code=400)

# Routes turati
@app.get("/sostituzioni/turati/today/{classe}", tags=["Sostituzioni"])
@limiter.limit("1/second")
def sostituzioni_turati_today(request: Request, response: Response, classe: str):
    # Check if the class is valid
    if classe != None:
        sostituzioni = Sostituzioni("https://www.rapisardidavinci.edu.it/sost/app/sostituzioni2.php")
        updates = sostituzioni.getTodayUpdatesFromClass(classe)
        if updates != "null" and updates != None:
            return JSONResponse(content={"message": updates, "status": "success", "code": 200}, status_code=200)
        else:
            return JSONResponse(content={"message": "No updates", "status": "error", "code": 404}, status_code=404)

    return JSONResponse(content={"message": "Invalid class", "status": "error", "code": 400}, status_code=400)

@app.get("/sostituzioni/turati/next/{classe}", tags=["Sostituzioni"])
@limiter.limit("1/second")
def sostituzioni_turati_next(request: Request, response: Response, classe: str):
    # Check if the class is valid
    if classe != None:
        sostituzioni = Sostituzioni("https://www.rapisardidavinci.edu.it/sost/app/sostituzioni2.php")
        updates = sostituzioni.getNextUpdatesFromClass(classe)
        if updates != "null" and updates != None:
            return JSONResponse(content={"message": updates, "status": "success", "code": 200}, status_code=200)
        else:
            return JSONResponse(content={"message": "No updates", "status": "error", "code": 404}, status_code=404)

    return JSONResponse(content={"message": "Invalid class", "status": "error", "code": 400}, status_code=400)

# Routes serale
@app.get("/sostituzioni/serale/today/{classe}", tags=["Sostituzioni"])
@limiter.limit("1/second")
def sostituzioni_serale_today(request: Request, response: Response, classe: str):
    # Check if the class is valid
    if classe != None:
        sostituzioni = Sostituzioni("https://www.rapisardidavinci.edu.it/sost/app/sostituzioni3.php")
        updates = sostituzioni.getTodayUpdatesFromClass(classe)
        if updates != "null" and updates != None:
            return JSONResponse(content={"message": updates, "status": "success", "code": 200}, status_code=200)
        else:
            return JSONResponse(content={"message": "No updates", "status": "error", "code": 404}, status_code=404)

    return JSONResponse(content={"message": "Invalid class", "status": "error", "code": 400}, status_code=400)

@app.get("/sostituzioni/serale/next/{classe}", tags=["Sostituzioni"])
@limiter.limit("1/second")
def sostituzioni_serale_next(request: Request, response: Response, classe: str):
    # Check if the class is valid
    if classe != None:
        sostituzioni = Sostituzioni("https://www.rapisardidavinci.edu.it/sost/app/sostituzioni3.php")
        updates = sostituzioni.getNextUpdatesFromClass(classe)
        if updates != "null" and updates != None:
            return JSONResponse(content={"message": updates, "status": "success", "code": 200}, status_code=200)
        else:
            return JSONResponse(content={"message": "No updates", "status": "error", "code": 404}, status_code=404)

    return JSONResponse(content={"message": "Invalid class", "status": "error", "code": 400}, status_code=400)

# Routes all
@app.get("/sostituzioni/margherita/all", tags=["Sostituzioni"])
@limiter.limit("1/second")
def sostituzioni_margherita_all(request: Request, response: Response):
    sostituzioni = Sostituzioni("https://www.rapisardidavinci.edu.it/sost/app/sostituzioni.php")
    updates = sostituzioni.getAllUpdates()
    if updates != "null" and updates != None:
        return JSONResponse(content={"message": updates, "status": "success", "code": 200}, status_code=200)
    else:
        return JSONResponse(content={"message": "No updates", "status": "error", "code": 404}, status_code=404)


@app.get("/sostituzioni/turati/all", tags=["Sostituzioni"])
@limiter.limit("1/second")
def sostituzioni_turati_all(request: Request, response: Response):
    sostituzioni = Sostituzioni("https://www.rapisardidavinci.edu.it/sost/app/sostituzioni2.php")
    updates = sostituzioni.getAllUpdates()
    if updates != "null" and updates != None:
        return JSONResponse(content={"message": updates, "status": "success", "code": 200}, status_code=200)
    else:
        return JSONResponse(content={"message": "No updates", "status": "error", "code": 404}, status_code=404)
    
@app.get("/sostituzioni/serale/all", tags=["Sostituzioni"])
@limiter.limit("1/second")
def sostituzioni_serale_all(request: Request, response: Response):
    sostituzioni = Sostituzioni("https://www.rapisardidavinci.edu.it/sost/app/sostituzioni3.php")
    updates = sostituzioni.getAllUpdates()
    if updates != "null" and updates != None:
        return JSONResponse(content={"message": updates, "status": "success", "code": 200}, status_code=200)
    else:
        return JSONResponse(content={"message": "No updates", "status": "error", "code": 404}, status_code=404)
    
@app.get("/orario/classi/all", tags=["Orario"])
@limiter.limit("1/second")
def orario_classi_all(request: Request, response: Response, onlyNames: bool = False):
    orario = Orario("https://www.rapisardidavinci.edu.it/orario/")
    orario = orario.getAllClassesTimetable(onlyNames)

    return JSONResponse(content={"message": orario, "status": "success", "code": 200}, status_code=200)

@app.get("/orario/docenti/all", tags=["Orario"])
@limiter.limit("1/second")
def orario_docenti_all(request: Request, response: Response, onlyNames: bool = False):
    orario = Orario("https://www.rapisardidavinci.edu.it/orario/")
    orario = orario.getAllDocentiTimetable(onlyNames)

    return JSONResponse(content={"message": orario, "status": "success", "code": 200}, status_code=200)

@app.get("/orario/aule/all", tags=["Orario"])
@limiter.limit("1/second")
def orario_laboratori_all(request: Request, response: Response, onlyNames: bool = False):
    orario = Orario("https://www.rapisardidavinci.edu.it/orario/")
    orario = orario.getAllAuleTimetable(onlyNames)

    return JSONResponse(content={"message": orario, "status": "success", "code": 200}, status_code=200)

@app.get("/dashboard/", tags=["Dashboard"])
@limiter.limit("2/second")
def dashboard(request: Request, response: Response):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/dashboard/", tags=["Dashboard"])
@limiter.limit("2/second")
def dashboard(request: Request, response: Response, email: str = Form(...), classe: str = Form(None), delete: str = Form(None)):
    print("Email: " + str(email))
    print("Classe: " + str(classe))
    print("Delete: " + str(delete))

    # Check if email in form
    if email == None or email == "":
        return templates.TemplateResponse("dashboard.html", {"request": request, "error": "Email not set"})

    # Check if email is valid
    if "@" not in email or "." not in email:
        return templates.TemplateResponse("dashboard.html", {"request": request, "error": "Invalid email"})

    # Check if email is already in the database
    user = DATABASE.getUserFromEmail(email)
    if user != None:
        if delete != None and delete == True or delete == "true":
            print("Deleting " + str(classe) + " from " + email)
            # Delete the class from the user
            if DATABASE.deleteClassFromUser(email, classe):
                user = DATABASE.getUserFromEmail(email)
                return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "success": "Class deleted"})
            else:
                return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "error": "Class not found"})
        elif delete != None and delete == False or delete == "false":
            print("Adding " + str(classe) + " to " + email)
            # Add the class to the user
            if DATABASE.addClassToUser(email, classe):
                user = DATABASE.getUserFromEmail(email)
                return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "success": "Class added"})
            else:
                return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "error": "Class not found"})
    
        else:
            return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

    return templates.TemplateResponse("dashboard.html", {"request": request, "error": "User not found"})


# Home
start_time = datetime.datetime.now() # For the uptime

@app.get("/status", tags=["Status"])
@limiter.limit("1/second")
def api_status(request: Request, response: Response):
    # Get the API uptime without microseconds
    uptime = datetime.datetime.now() - start_time
    uptime = str(uptime).split(".")[0]

    url = request.url
    url = url.scheme + "://" + url.netloc

    message = "The Rapisardi Notifications API is up and running. Check the documentation at " + url + "/docs or " + url + "/redoc for more information. By @Matt0550 (GitHub)"

    response.status_code = status.HTTP_200_OK

    return {"message": message, "uptime": uptime, "status": "success", "code": response.status_code, "url": url}

@app.get('/', tags=["Status"])
@limiter.limit("1/second")
def home(request: Request, response: Response):
    return api_status(request, response)

def updateDb():
    # Run update_db.py in a new thread
    thread = Thread(target=os.system, args=("python update_db.py",))
    thread.start()

# Exclude from docs
@app.post('/admin/update_db', tags=["Admin"], include_in_schema=False)
@limiter.limit("1/second")
async def update_db(request: Request, response: Response, token: str = Form(...)):
    if token != None:
        print("Checking for updates " + str(request.client.host))
        # Check if the request is from localhost
        if token == os.environ["ADMIN_TOKEN"]:
            # Check for updates
            updateDb()
            return JSONResponse(content={"message": "Success triggering update_db", "status": "success", "code": 200}, status_code=200)
        else:
            return JSONResponse(content={"message": "Unauthorized", "status": "error", "code": 401}, status_code=401)
    else:
        return JSONResponse(content={"message": "Unauthorized", "status": "error", "code": 400}, status_code=400)

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")