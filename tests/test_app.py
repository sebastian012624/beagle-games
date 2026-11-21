import re

from fastapi.testclient import TestClient

from app.catalog import GAMES, recommend_games
from app.main import app

client = TestClient(app)


def test_recommendations_respect_genre_budget_and_pc_level():
    results = recommend_games("RPG", "Bajo", 60_000)
    assert results
    assert all(game["genre"] == "RPG" for game in results)
    assert all(game["level"] == "Bajo" and game["price"] <= 60_000 for game in results)


def test_catalog_route_renders_games_and_price():
    response = client.get("/")
    assert response.status_code == 200
    assert "Stardew Valley" in response.text
    assert "El catálogo" in response.text


def test_stylesheet_is_served():
    response = client.get("/static/styles.css")
    assert response.status_code == 200
    assert "--orange" in response.text
    assert client.get("/static/catalog.css").status_code == 200


def test_all_catalog_covers_are_available():
    for game in GAMES:
        response = client.get(game["cover"])
        assert response.status_code == 200, game["name"]
        assert response.headers["content-type"] == "image/jpeg"


def test_every_catalog_card_shows_a_price():
    html = client.get("/").text
    cards = re.findall(r'<article class="game-card">(.*?)</article>', html, re.DOTALL)
    assert len(cards) == len(GAMES)
    for game in GAMES:
        card = next(card for card in cards if f"/carrito/agregar/{game['id']}" in card)
        assert game["price"] > 0, game["name"]
        price = f"${game['price']:,}".replace(",", ".")
        assert f"{price}" in re.search(r'<div class="game-buy">(.*?)</div>', card, re.DOTALL).group(1), game["name"]
        assert "cover-price" not in card, game["name"]
        assert "Gratis" not in card, game["name"]


def test_catalog_search_matches_game_title_and_keeps_genre_filter():
    response = client.get("/", params={"genre": "Aventura", "q": "Firewatch"})
    assert response.status_code == 200
    assert "Firewatch" in response.text
    assert "Machinarium" not in response.text
    assert "1 JUEGOS" in response.text


def test_catalog_can_sort_by_price_low_to_high():
    response = client.get("/", params={"sort": "price_asc"})
    cards = re.findall(r'<article class="game-card">(.*?)</article>', response.text, re.DOTALL)
    displayed_ids = [re.search(r"/carrito/agregar/([^\"]+)", card).group(1) for card in cards]
    expected_ids = [
        game["id"]
        for game in sorted(GAMES, key=lambda game: (game["price"], game["name"].casefold()))
    ]
    assert displayed_ids == expected_ids


def test_add_to_cart_and_checkout_show_total_and_clear_cart():
    with TestClient(app) as browser:
        browser.post("/carrito/agregar/stardew-valley", follow_redirects=False)
        browser.post("/carrito/agregar/undertale", follow_redirects=False)
        response = browser.post("/pagar", follow_redirects=True)
        assert response.status_code == 200
        assert "¡Juegos comprados!" in response.text
        assert "$100.000" in response.text
        assert "Stardew Valley" in response.text
        assert browser.get("/").text.count("Stardew Valley") == 3  # título, etiqueta y texto alternativo


def test_invalid_game_does_not_enter_cart():
    with TestClient(app) as browser:
        browser.post("/carrito/agregar/no-es-un-juego", follow_redirects=False)
        response = browser.get("/")
        assert response.status_code == 200
        assert "No encontramos ese juego" in response.text
        assert "Tu carrito está esperando" in response.text


def test_recommend_route_handles_invalid_budget():
    response = client.post("/recomendar", data={"genre": "RPG", "pc_level": "Alto", "budget": -1})
    assert response.status_code == 200
    assert "presupuesto entre $0" in response.text


def test_catalog_has_unique_ids_and_valid_prices():
    ids = [game["id"] for game in GAMES]
    assert len(ids) == len(set(ids))
    assert all(game["price"] > 0 for game in GAMES)
