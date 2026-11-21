"""FastAPI routes for the Beagle Games storefront."""

from datetime import datetime
import os
from secrets import token_hex

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.catalog import BY_ID, GAMES, GENRES, LEVELS, recommend_games

app = FastAPI(title="Beagle Games", description="Tienda y recomendador de videojuegos")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "local-only-beagle-games-secret"),
)
templates = Jinja2Templates(directory="app/templates")
SORT_OPTIONS = {
    "name": "Nombre (A–Z)",
    "price_asc": "Precio: menor a mayor",
    "price_desc": "Precio: mayor a menor",
}


def cart_items(request: Request) -> list[dict]:
    ids = request.session.get("cart", [])
    return [BY_ID[game_id] for game_id in ids if game_id in BY_ID]


def render_store(request: Request, **context):
    cart = cart_items(request)
    order = request.session.pop("order", None)
    if order:
        order["games"] = [BY_ID[game_id] for game_id in order.pop("game_ids", []) if game_id in BY_ID]
    base = {
        "request": request,
        "games": GAMES,
        "genres": GENRES,
        "sort_options": SORT_OPTIONS,
        "cart": cart,
        "cart_total": sum(game["price"] for game in cart),
        "cart_count": len(cart),
        "notice": request.session.pop("notice", None),
        "order": order,
    }
    base.update(context)
    return templates.TemplateResponse(request=request, name="index.html", context=base)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, genre: str = "Todos", q: str = "", sort: str = "name"):
    selected = genre if genre in GENRES else "Todos"
    visible = GAMES if selected == "Todos" else [game for game in GAMES if game["genre"] == selected]
    search_term = q.strip()
    if search_term:
        needle = search_term.casefold()
        visible = [game for game in visible if needle in game["name"].casefold()]
    selected_sort = sort if sort in SORT_OPTIONS else "name"
    if selected_sort == "price_asc":
        visible = sorted(visible, key=lambda game: (game["price"], game["name"].casefold()))
    elif selected_sort == "price_desc":
        visible = sorted(visible, key=lambda game: (-game["price"], game["name"].casefold()))
    else:
        visible = sorted(visible, key=lambda game: game["name"].casefold())
    return render_store(
        request,
        visible_games=visible,
        selected_genre=selected,
        search_term=search_term,
        sort_by=selected_sort,
    )


@app.post("/carrito/agregar/{game_id}")
async def add_to_cart(request: Request, game_id: str):
    if game_id not in BY_ID:
        request.session["notice"] = "No encontramos ese juego en el catálogo."
    else:
        cart = request.session.get("cart", [])
        if game_id not in cart:
            cart.append(game_id)
        request.session["cart"] = cart
        request.session["notice"] = f"{BY_ID[game_id]['name']} se agregó a tu carrito."
    return RedirectResponse(url="/#catalogo", status_code=303)


@app.post("/carrito/quitar/{game_id}")
async def remove_from_cart(request: Request, game_id: str):
    request.session["cart"] = [item for item in request.session.get("cart", []) if item != game_id]
    return RedirectResponse(url="/#carrito", status_code=303)


@app.post("/pagar")
async def checkout(request: Request):
    cart = cart_items(request)
    if not cart:
        request.session["notice"] = "Agrega al menos un juego antes de continuar."
        return RedirectResponse(url="/#carrito", status_code=303)
    request.session["order"] = {
        "game_ids": [game["id"] for game in cart],
        "total": sum(game["price"] for game in cart),
        "reference": f"BG-{datetime.now():%Y%m%d}-{token_hex(2).upper()}",
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    request.session["cart"] = []
    return RedirectResponse(url="/#comprobante", status_code=303)


@app.post("/recomendar", response_class=HTMLResponse)
async def recommend(
    request: Request,
    genre: str = Form(...),
    pc_level: str = Form(...),
    budget: int = Form(...),
):
    error = None
    results = []
    if genre not in GENRES[1:] or pc_level not in LEVELS:
        error = "Elige un género y un perfil de PC válidos."
    elif budget < 0 or budget > 10_000_000:
        error = "Escribe un presupuesto entre $0 y $10.000.000 COP."
    else:
        results = recommend_games(genre, pc_level, budget)
    return render_store(
        request,
        visible_games=GAMES,
        selected_genre="Todos",
        search_term="",
        sort_by="name",
        recommendation=results,
        recommendation_error=error,
        recommendation_query={"genre": genre, "pc_level": pc_level, "budget": budget},
    )
