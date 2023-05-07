###########################################################
# ITET Rapisardi da Vinci - Sostituzioni API (Unofficial) #
###########################################################

# Created by: @Matt0550 (GitHub)

# FastAPI
import atexit
import datetime
import os
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler


from Sostituzioni import Sostituzioni
# Init 
app = FastAPI()
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
    
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(content={"message": "Rate limit exceeded. Try again in " + str(exc.retry_after) + " seconds", "status": "error", "code": 429}, status_code=429)

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

    message = "StudyApp: The Rapisardi integration is working correctly"

    response.status_code = status.HTTP_200_OK

    return {"message": message, "uptime": uptime, "status": "success", "code": response.status_code, "url": url}

@app.get('/', tags=["Status"])
@limiter.limit("1/second")
def home(request: Request, response: Response):
    return api_status(request, response)

def update_db():
    # Run the update_db.py script
    os.system("python3 update_db.py")

# Run file update_db.py every hour
scheduler = BackgroundScheduler()
scheduler.add_job(update_db, 'interval', hours=1)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")