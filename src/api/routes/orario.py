###########################################################
# ITET Rapisardi da Vinci - Sostituzioni API (Unofficial) #
###########################################################

# Created by: @Matt0550 (GitHub)
# Orario routes

from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import Response

from scrapers.orario import Orario
from core.config import settings


router = APIRouter()

orario = Orario(settings.ORARIO_URL)

@router.get("/classi/all")
def orario_classi_all(request: Request, response: Response, onlyNames: bool = False):
    return orario.getAllClassesTimetable(onlyNames)

@router.get("/docenti/all")
def orario_docenti_all(request: Request, response: Response, onlyNames: bool = False):
    return orario.getAllDocentiTimetable(onlyNames)

@router.get("/aule/all")
def orario_laboratori_all(request: Request, response: Response, onlyNames: bool = False):
    return orario.getAllAuleTimetable(onlyNames)

@router.get("/sostegno/all")
def orario_sostegno_all(request: Request, response: Response):
    return orario.getSostegnoTimetable()