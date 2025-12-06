###########################################################
# ITET Rapisardi da Vinci - Sostituzioni API (Unofficial) #
###########################################################

# Created by: @Matt0550 (GitHub)
# Sostituzioni routes

from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import Response

from scrapers.sostituzioni import Sostituzioni
from core.config import settings

router = APIRouter()

sostituzioni_margherita = Sostituzioni(settings.SOSTITUZIONI_MARGHERITA_URL)
sostituzioni_turati = Sostituzioni(settings.SOSTITUZIONI_TURATI_URL)
sostituzioni_serale = Sostituzioni(settings.SOSTITUZIONI_SERALE_URL)

# Routes margherita
@router.get("/margherita/today/{classe}")
def sostituzioni_margherita_today(request: Request, response: Response, classe: str):
    # Check if the class is valid
    if classe is not None:
        updates = sostituzioni_margherita.getTodayUpdatesFromClass(classe)
        if updates != "null" and updates is not None:
            return updates
        else:
            raise HTTPException(status_code=404, detail="No updates")

    raise HTTPException(status_code=400, detail="Invalid class")

@router.get("/margherita/next/{classe}")
def sostituzioni_margherita_next(request: Request, response: Response, classe: str):
    # Check if the class is valid
    if classe is not None:
        updates = sostituzioni_margherita.getNextUpdatesFromClass(classe)
        if updates != "null" and updates is not None:
            return updates
        else:
            raise HTTPException(status_code=404, detail="No updates")
    raise HTTPException(status_code=400, detail="Invalid class")

# Routes turati
@router.get("/turati/today/{classe}")
def sostituzioni_turati_today(request: Request, response: Response, classe: str):
    # Check if the class is valid
    if classe is not None:
        updates = sostituzioni_turati.getTodayUpdatesFromClass(classe)
        if updates != "null" and updates is not None:
            return updates
        else:
            raise HTTPException(status_code=404, detail="No updates")
    raise HTTPException(status_code=400, detail="Invalid class")

@router.get("/turati/next/{classe}")
def sostituzioni_turati_next(request: Request, response: Response, classe: str):
    # Check if the class is valid
    if classe is not None:
        updates = sostituzioni_turati.getNextUpdatesFromClass(classe)
        if updates != "null" and updates is not None:
            return updates
        else:
            raise HTTPException(status_code=404, detail="No updates")
    raise HTTPException(status_code=400, detail="Invalid class")

# Routes serale
@router.get("/serale/today/{classe}")
def sostituzioni_serale_today(request: Request, response: Response, classe: str):
    # Check if the class is valid
    if classe is not None:
        updates = sostituzioni_serale.getTodayUpdatesFromClass(classe)
        if updates != "null" and updates is not None:
            return updates
        else:
            raise HTTPException(status_code=404, detail="No updates")

    raise HTTPException(status_code=400, detail="Invalid class")

@router.get("/serale/next/{classe}")
def sostituzioni_serale_next(request: Request, response: Response, classe: str):
    if classe is not None:
        updates = sostituzioni_serale.getNextUpdatesFromClass(classe)
        if updates != "null" and updates is not None:
            return updates
        else:
            raise HTTPException(status_code=404, detail="No updates")
    raise HTTPException(status_code=400, detail="Invalid class")

# Routes all
@router.get("/margherita/all")
def sostituzioni_margherita_all(request: Request, response: Response):
    updates = sostituzioni_margherita.getAllUpdates()
    if updates != "null" and updates is not None:
        return updates
    else:
        raise HTTPException(status_code=404, detail="No updates")


@router.get("/turati/all")
def sostituzioni_turati_all(request: Request, response: Response):
    updates = sostituzioni_turati.getAllUpdates()
    if updates != "null" and updates is not None:
        return updates
    else:
        raise HTTPException(status_code=404, detail="No updates")
    
@router.get("/serale/all")
def sostituzioni_serale_all(request: Request, response: Response):
    updates = sostituzioni_serale.getAllUpdates()
    if updates != "null" and updates is not None:
        return updates
    else:
        raise HTTPException(status_code=404, detail="No updates")