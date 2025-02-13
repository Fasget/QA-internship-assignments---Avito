import pytest
import requests

BASE_URL = "https://qa-internship.avito.com/api/1"

EXISTING_AD_ID = "0cd4183f-a699-4486-83f8-b513dfde477a"  # пример из коллекции
EXISTING_SELLER_ID = 1234345231  # пример из коллекции

def test_1_create_item_success():
    """
    Успешное создание объявления (POST /api/1/item).
    По Postman: Ожидаем код 200, тело: {"status": "<string>"}.
    """
    payload = {
        "sellerID": EXISTING_SELLER_ID,
        "name": "dsds",
        "price": 1,
        "statistics": {
            "contacts": 3,
            "likes": 123,
            "viewCount": 12
        }
    }
    resp = requests.post(f"{BASE_URL}/item", json=payload)
    assert resp.status_code == 200, f"Ожидаем 200, получен {resp.status_code}"

    data = resp.json()
    assert "status" in data, "В ответе нет поля 'status'"
    


def test_2_create_item_invalid_seller_id():
    """
    Создание объявления с некорректным sellerID -> ожидаем 400 Bad Request.
    По Postman: тело будет содержать "result" и "status".
    """
    payload = {
        "sellerID": "abc123",  # некорректный (строка вместо int)
        "name": "TestInvalidSeller",
        "price": 100
    }
    resp = requests.post(f"{BASE_URL}/item", json=payload)
    assert resp.status_code == 400, f"Ожидаем 400, получен {resp.status_code}"

    data = resp.json()
    assert "result" in data, "Ожидаем поле 'result' в ответе"
    assert "status" in data, "Ожидаем поле 'status' в ответе"


def test_3_create_item_missing_required_field():
    """
    Создание объявления без обязательных полей -> ожидаем 400 Bad Request.
    По Postman: тело будет содержать "result" и "status".
    """
    payload = {
        "sellerID": EXISTING_SELLER_ID
        # "name" пропущено
        # "price" пропущено
    }
    resp = requests.post(f"{BASE_URL}/item", json=payload)
    assert resp.status_code == 400, f"Ожидаем 400, получен {resp.status_code}"

    data = resp.json()
    assert "result" in data, "Ожидаем поле 'result' в ответе"
    assert "status" in data, "Ожидаем поле 'status' в ответе"


def test_4_get_item_success():
    """
    Успешное получение объявления (GET /api/1/item/:id).
    По Postman: 200 OK -> массив объектов, каждый объект: {id, sellerId, name, price, statistics, createdAt}.
    """
    resp = requests.get(f"{BASE_URL}/item/{EXISTING_AD_ID}")
    assert resp.status_code == 200, f"Ожидаем 200, получен {resp.status_code}"

    data = resp.json()
    assert isinstance(data, list), "Ожидаем, что придёт список объектов"
    assert len(data) > 0, "Список объявлений пуст, хотя ожидали минимум одно"

    first_item = data[0]
    for field in ["id", "sellerId", "name", "price", "statistics", "createdAt"]:
        assert field in first_item, f"В объекте нет поля '{field}'"


def test_5_get_item_not_found():
    """
    Запрос несуществующего объявления -> 404 Not Found.
    Тело содержит { "result": {...}, "status": "<string>" }
    """
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = requests.get(f"{BASE_URL}/item/{fake_id}")
    assert resp.status_code == 404, f"Ожидаем 404, получен {resp.status_code}"

    data = resp.json()
    assert "result" in data, "Ожидаем 'result' в ответе"
    assert "status" in data, "Ожидаем 'status' в ответе"


def test_6_get_item_invalid_id_format():
    """
    Некорректный формат ID (невалидный UUID).
    По логике, ожидаем либо 400 Bad Request, либо 404 Not Found.
    """
    invalid_id = "12345"
    resp = requests.get(f"{BASE_URL}/item/{invalid_id}")

    assert resp.status_code in (400, 404), f"Ожидаем 400 или 404, а получили {resp.status_code}"

    data = resp.json()
    assert "result" in data, "Ожидаем 'result' в ответе"
    assert "status" in data, "Ожидаем 'status' в ответе"


def test_7_get_items_by_seller():
    """
    Получение объявлений для существующего продавца (GET /api/1/:sellerID/item).
    Ожидаем 200 OK и массив объектов.
    """
    resp = requests.get(f"{BASE_URL}/{EXISTING_SELLER_ID}/item")
    assert resp.status_code == 200, f"Ожидаем 200, получен {resp.status_code}"

    data = resp.json()
    assert isinstance(data, list), "Ожидаем, что ответ содержит список объявлений"
    if len(data) > 0:
        first_item = data[0]
        for field in ["id", "sellerId", "name", "price", "statistics", "createdAt"]:
            assert field in first_item, f"В объявлении нет поля '{field}'"


def test_8_get_items_by_seller_invalid_format():
    """
    Запрос с некорректным форматом sellerID (не число или вообще неправильное).
    По Postman: ожидаем 400 Bad request.
    """
    resp = requests.get(f"{BASE_URL}/abc123/item")
    assert resp.status_code == 400, f"Ожидаем 400, получен {resp.status_code}"

    data = resp.json()
    assert "result" in data, "Ожидаем поле 'result'"
    assert "status" in data, "Ожидаем поле 'status'"


def test_9_get_items_by_seller_no_items():
    """
    Получение объявлений, если у продавца их нет.
    По логике: код 200 OK и пустой массив.
    """
    seller_id_without_ads = "9"  # допустим, у него нет объявлений
    resp = requests.get(f"{BASE_URL}/{seller_id_without_ads}/item")
    assert resp.status_code == 200, f"Ожидаем 200, получен {resp.status_code}"

    data = resp.json()
    assert isinstance(data, list), "Ожидаем список"
    assert len(data) == 0, "Ожидаем пустой массив, но пришло что-то"


def test_10_get_statistic_success():
    """
    Успешное получение статистики по существующему объявлению.
    По Postman: 200 OK, тело - массив объектов [{ likes, viewCount, contacts }, ...].
    """
    resp = requests.get(f"{BASE_URL}/statistic/{EXISTING_AD_ID}")
    assert resp.status_code == 200, f"Ожидаем 200, получен {resp.status_code}"

    data = resp.json()
    assert isinstance(data, list), "Ожидаем, что ответ - массив"
    assert len(data) > 0, "Ожидаем в массиве хотя бы один объект статистики"

    stat_obj = data[0]
    for field in ["likes", "viewCount", "contacts"]:
        assert field in stat_obj, f"Ожидаем поле '{field}' в статистике"


def test_11_get_statistic_not_found():
    """
    Запрос статистики для несуществующего объявления -> 404 Bad Request.
    Тело: { "result": {...}, "status": "<string>" }
    """
    fake_id = "00000000-0000-0000-0000-000000000001"
    resp = requests.get(f"{BASE_URL}/statistic/{fake_id}")
    assert resp.status_code == 404, f"Ожидаем 404, получен {resp.status_code}"

    data = resp.json()
    assert "result" in data, "Ожидаем 'result'"
    assert "status" in data, "Ожидаем 'status'"


def test_12_get_statistic_invalid_id_format():
    """
    Некорректный формат ID при запросе статистики.
    Можно ждать 400 Bad Request или 404 Not Found.
    """
    invalid_id = "not-uuid"
    resp = requests.get(f"{BASE_URL}/statistic/{invalid_id}")
    assert resp.status_code in (400, 404), f"Ожидаем 400 или 404, получен {resp.status_code}"

    data = resp.json()
    assert "result" in data, "Ожидаем 'result' в ответе"
    assert "status" in data, "Ожидаем 'status' в ответе"
