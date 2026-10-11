"""FastAPI web layer."""
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from app.weather_api import get_current_weather, WeatherAPIError

app = FastAPI(title="Погода за назвою міста")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"weather": None, "error": None, "city": ""},
    )


@app.post("/weather", response_class=HTMLResponse)
def weather_page(request: Request, city: str = Form(...)):
    city = city.strip()
    weather = None
    error = None
    try:
        weather = get_current_weather(city)
    except ValueError as exc:
        error = str(exc)
    except LookupError as exc:
        error = str(exc)
    except WeatherAPIError as exc:
        error = str(exc)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"weather": weather, "error": error, "city": city},
    )


@app.get("/api/weather")
def weather_json(city: str = ""):
    city = city.strip()
    if not city:
        return JSONResponse(status_code=400, content={"detail": "Вкажіть назву міста в параметрі city."})
    try:
        return get_current_weather(city)
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    except LookupError as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    except WeatherAPIError as exc:
        return JSONResponse(status_code=502, content={"detail": str(exc)})
