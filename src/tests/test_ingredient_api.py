# tests/test_ingredients_api.py
from fastapi.testclient import TestClient

def _create(client: TestClient, **over):
    payload = {
        "name": "Oats",
        "kcal_per_100g": 389.0,
        "carbs_per_100g": 66.0,
        "fats_per_100g": 6.9,
        "proteins_per_100g": 16.9,
    }
    payload.update(over)
    r = client.post("/ingredients", json=payload)
    return r

def test_create_ok(app):
    client = TestClient(app)
    r = _create(client)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["id"] >= 1
    assert body["name"] == "Oats"

def test_create_validation_error_maps_to_404_per_current_router(app):
    # NOTE: your router maps ValidationError -> 404 (usually this should be 400).
    client = TestClient(app)
    r = _create(client, name="")  # invalid
    assert r.status_code == 404
    assert "bad data" in r.json().get("detail", "").lower()

def test_search_ok(app):
    client = TestClient(app)
    _ = _create(client, name="Oats")
    _ = _create(client, name="Oat Milk")
    _ = _create(client, name="Rice")

    r = client.get("/ingredients/search", params={"q": "oat", "limit": 10})
    assert r.status_code == 200
    names = [x["name"] for x in r.json()]
    assert "Oats" in names and "Oat Milk" in names and "Rice" not in names

def test_get_ok(app):
    client = TestClient(app)
    r1 = _create(client, name="Honey")
    _id = r1.json()["id"]

    # ⚠ Your code currently decorates GET as "/{ingredients_id}" but the function arg is "ingredient_id".
    # That mismatch makes FastAPI return 422. After fixing the router (see notes below), this will pass.
    r = client.get(f"/ingredients/{_id}")
    assert r.status_code == 200, r.text
    assert r.json()["name"] == "Honey"

def test_get_not_found_maps_to_404(app):
    client = TestClient(app)
    r = client.get("/ingredients/999999")
    assert r.status_code == 404
    assert "couldn't find" in r.json().get("detail", "").lower()

def test_put_update_ok(app):
    client = TestClient(app)
    r1 = _create(client, name="Apple", kcal_per_100g=52, carbs_per_100g=14, fats_per_100g=0.2, proteins_per_100g=0.3)
    _id = r1.json()["id"]

    update = {"name": "Apple (raw)", "kcal_per_100g": 52, "carbs_per_100g": 14, "fats_per_100g": 0.2, "proteins_per_100g": 0.3}
    # ⚠ Your code currently decorates PUT as "/{ingredien_id}" (typo) while the function arg is "ingredient_id".
    r = client.put(f"/ingredients/{_id}", json=update)
    assert r.status_code == 200, r.text
    assert r.json()["name"] == "Apple (raw)"

def test_put_validation_error_maps_to_404(app):
    client = TestClient(app)
    r1 = _create(client, name="Banana")
    _id = r1.json()["id"]

    update = {"name": "", "kcal_per_100g": 1, "carbs_per_100g": 1, "fats_per_100g": 1, "proteins_per_100g": 1}
    r = client.put(f"/ingredients/{_id}", json=update)
    assert r.status_code == 404  # per your router's handling

def test_delete_ok(app):
    client = TestClient(app)
    r1 = _create(client, name="ToDelete")
    _id = r1.json()["id"]

    r = client.delete(f"/ingredients/{_id}")
    assert r.status_code == 204

    # subsequent GET -> 404
    r2 = client.get(f"/ingredients/{_id}")
    assert r2.status_code == 404

def test_delete_missing_maps_to_404(app):
    client = TestClient(app)
    r = client.delete("/ingredients/999999")
    assert r.status_code == 404
