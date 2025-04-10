import pytest
import requests

BASE_URL_V1 = "https://qa-internship.avito.com/api/1"
BASE_URL_V2 = "https://qa-internship.avito.com/api/2"

EXISTING_AD_ID = "0cd4183f-a699-4486-83f8-b513dfde477a"
EXISTING_SELLER_ID = 1234345231

def create_item(payload):
    """
    Отправляет POST запрос для создания объявления через API версии 1.
    """
    url = f"{BASE_URL_V1}/item"
    return requests.post(url, json=payload)

def get_item_by_id(item_id, version="v1"):
    """
    Отправляет GET запрос для получения объявления по id.
    """
    if version == "v1":
        url = f"{BASE_URL_V1}/item/{item_id}"
    else:
        url = f"{BASE_URL_V2}/item/{item_id}"
    return requests.get(url)

def get_items_by_seller(seller_id):
    """
    Отправляет GET запрос для получения всех объявлений конкретного продавца через API V1.
    """
    url = f"{BASE_URL_V1}/{seller_id}/item"
    return requests.get(url)

def get_statistic_by_id(item_id, version="v1"):
    """
    Отправляет GET запрос для получения статистики объявления.
    """
    if version == "v1":
        url = f"{BASE_URL_V1}/statistic/{item_id}"
    elif version == "v2":
        url = f"{BASE_URL_V2}/statistic/{item_id}"
    else:
        raise ValueError("Unsupported version")
    return requests.get(url)

def delete_item(item_id):
    """
    Отправляет DELETE запрос для удаления объявления через API V2.
       """
    url = f"{BASE_URL_V2}/item/{item_id}"
    return requests.delete(url)

def extract_id_from_status(status_str):
    """
    Извлекает UUID объявления из строки.
    """
    parts = status_str.split(" - ")
    return parts[-1].strip() if len(parts) > 1 else None


def test_1_create_item_success():
    """Успешное создание объявления (POST /api/1/item)."""
    payload = {
        "sellerID": EXISTING_SELLER_ID,
        "name": "dsds",
        "price": 1,
        "statistics": {"contacts": 3, "likes": 123, "viewCount": 12}
    }
    resp = create_item(payload)
    assert resp.status_code == 200, f"Ожидаем 200, получен {resp.status_code}"
    data = resp.json()
    assert "status" in data, "В ответе нет поля 'status'"


def test_2_create_item_invalid_seller_id():
    """Создание объявления с некорректным sellerID -> ожидаем 400 Bad Request."""
    payload = {
        "sellerID": "abc123",  # некорректный тип
        "name": "TestInvalidSeller",
        "price": 100
    }
    resp = create_item(payload)
    assert resp.status_code == 400, f"Ожидаем 400, получен {resp.status_code}"
    data = resp.json()
    assert "result" in data, "Ожидаем поле 'result' в ответе"
    assert "status" in data, "Ожидаем поле 'status' в ответе"


def test_3_create_item_missing_required_field():
    """Создание объявления без обязательных полей -> ожидаем 400 Bad Request."""
    payload = {"sellerID": EXISTING_SELLER_ID}  # поля name и price отсутствуют
    resp = create_item(payload)
    assert resp.status_code == 400, f"Ожидаем 400, получен {resp.status_code}"
    data = resp.json()
    assert "result" in data, "Ожидаем поле 'result' в ответе"
    assert "status" in data, "Ожидаем поле 'status' в ответе"


def test_4_get_item_success():
    """Успешное получение объявления (GET /api/1/item/:id)."""
    resp = get_item_by_id(EXISTING_AD_ID, version="v1")
    assert resp.status_code == 200, f"Ожидаем 200, получен {resp.status_code}"
    data = resp.json()
    assert isinstance(data, list), "Ожидаем, что ответ - массив объектов"
    assert len(data) > 0, "Массив объявлений пуст"
    for field in ["id", "sellerId", "name", "price", "statistics", "createdAt"]:
        assert field in data[0], f"В объявлении нет поля '{field}'"


def test_5_get_item_not_found():
    """Запрос несуществующего объявления -> 404 Not Found."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = get_item_by_id(fake_id, version="v1")
    assert resp.status_code == 404, f"Ожидаем 404, получен {resp.status_code}"
    data = resp.json()
    assert "result" in data, "Ожидаем 'result' в ответе"
    assert "status" in data, "Ожидаем 'status' в ответе"


def test_6_get_item_invalid_id_format():
    """Некорректный формат ID -> ожидаем 400 или 404."""
    invalid_id = "12345"
    resp = get_item_by_id(invalid_id, version="v1")
    assert resp.status_code in (400, 404), f"Ожидаем 400 или 404, получен {resp.status_code}"
    data = resp.json()
    assert "result" in data, "Ожидаем 'result' в ответе"
    assert "status" in data, "Ожидаем 'status' в ответе"


def test_7_get_items_by_seller():
    """Получение объявлений для существующего продавца (GET /api/1/:sellerID/item)."""
    resp = get_items_by_seller(EXISTING_SELLER_ID)
    assert resp.status_code == 200, f"Ожидаем 200, получен {resp.status_code}"
    data = resp.json()
    assert isinstance(data, list), "Ожидаем список объявлений"
    if data:
        for field in ["id", "sellerId", "name", "price", "statistics", "createdAt"]:
            assert field in data[0], f"В объявлении нет поля '{field}'"


def test_8_get_items_by_seller_invalid_format():
    """Запрос с некорректным форматом sellerID -> ожидаем 400."""
    resp = get_items_by_seller("abc123")
    assert resp.status_code == 400, f"Ожидаем 400, получен {resp.status_code}"
    data = resp.json()
    assert "result" in data, "Ожидаем поле 'result'"
    assert "status" in data, "Ожидаем поле 'status'"


def test_9_get_items_by_seller_no_items():
    """Получение объявлений, если у продавца их нет -> ожидаем пустой массив."""
    seller_id_without_ads = "9"
    resp = get_items_by_seller(seller_id_without_ads)
    assert resp.status_code == 200, f"Ожидаем 200, получен {resp.status_code}"
    data = resp.json()
    assert isinstance(data, list), "Ожидаем список"
    assert len(data) == 0, "Ожидаем пустой массив, но получены объявления"


def test_10_get_statistic_success_v1():
    """Успешное получение статистики по объявлению через V1 (GET /api/1/statistic/:id)."""
    resp = get_statistic_by_id(EXISTING_AD_ID, version="v1")
    assert resp.status_code == 200, f"Ожидаем 200, получен {resp.status_code}"
    data = resp.json()
    assert isinstance(data, list), "Ожидаем, что ответ - массив"
    assert data, "Ожидаем хотя бы один объект статистики"
    for field in ["likes", "viewCount", "contacts"]:
        assert field in data[0], f"Ожидаем поле '{field}' в статистике"


def test_11_get_statistic_not_found_v1():
    """Запрос статистики для несуществующего объявления через V1 -> 404 Not Found."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = get_statistic_by_id(fake_id, version="v1")
    assert resp.status_code == 404, f"Ожидаем 404, получен {resp.status_code}"
    data = resp.json()
    assert "result" in data, "Ожидаем 'result' в ответе"
    assert "status" in data, "Ожидаем 'status' в ответе"


def test_12_get_statistic_invalid_id_format_v1():
    """Некорректный формат ID для статистики через V1 -> ожидаем 400 или 404."""
    invalid_id = "not-uuid"
    resp = get_statistic_by_id(invalid_id, version="v1")
    assert resp.status_code in (400, 404), f"Ожидаем 400 или 404, получен {resp.status_code}"
    data = resp.json()
    assert "result" in data, "Ожидаем 'result' в ответе"
    assert "status" in data, "Ожидаем 'status' в ответе"


def test_13_get_statistic_success_v2():
    """Успешное получение статистики по объявлению через V2 (GET /api/2/statistic/:id)."""
    resp = get_statistic_by_id(EXISTING_AD_ID, version="v2")
    assert resp.status_code == 200, f"Ожидаем 200, получен {resp.status_code}"
    data = resp.json()
    assert isinstance(data, list), "Ожидаем, что ответ - массив"
    assert data, "Ожидаем хотя бы один объект статистики"
    for field in ["likes", "viewCount", "contacts"]:
        assert field in data[0], f"Ожидаем поле '{field}' в статистике"


def test_14_get_statistic_not_found_v2():
    """Запрос статистики для несуществующего объявления через V2 -> 404 Not Found."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = get_statistic_by_id(fake_id, version="v2")
    assert resp.status_code == 404, f"Ожидаем 404, получен {resp.status_code}"
    data = resp.json()
    assert "result" in data, "Ожидаем 'result' в ответе"
    assert "status" in data, "Ожидаем 'status' в ответе"


def test_15_get_statistic_invalid_id_format_v2():
    """Некорректный формат ID для статистики через V2 -> ожидаем 400 или 404."""
    invalid_id = "not-uuid"
    resp = get_statistic_by_id(invalid_id, version="v2")
    assert resp.status_code in (400, 404), f"Ожидаем 400 или 404, получен {resp.status_code}"
    data = resp.json()
    assert "result" in data, "Ожидаем 'result' в ответе"
    assert "status" in data, "Ожидаем 'status' в ответе"


def test_16_delete_existing_item():
    """Удаление ранее созданного объявления (DELETE /api/2/item/:id)."""
    payload = {
        "sellerID": 999999,
        "name": "Test Ad to Delete",
        "price": 123,
        "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
    }
    create_resp = create_item(payload)
    assert create_resp.status_code == 200, "Ошибка при создании объявления"
    data = create_resp.json()
    ad_id = data.get("id")
    assert ad_id, "Не получили id нового объявления"
    delete_resp = delete_item(ad_id)
    assert delete_resp.status_code == 200, f"Ожидаем 200, получен {delete_resp.status_code}"
    assert delete_resp.text == "", "Ожидаем пустое тело ответа после удаления"

def test_16_1_delete_existing_item_using_status_field():
    """Удаление объявления с использованием id, полученного из поля 'status'.
       Если поле 'id' отсутствует, ожидается, что 'status' содержит сообщение вида
       'Сохранили объявление - <uuid>', из которого можно извлечь id.
    """
    payload = {
        "sellerID": 999999,
        "name": "Test Ad to Delete",
        "price": 123,
        "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
    }
    create_resp = create_item(payload)
    assert create_resp.status_code == 200, "Ошибка при создании объявления"
    data = create_resp.json()
    ad_id = data.get("id")
    if not ad_id:
        status_str = data.get("status", "")
        assert status_str, "Не найдено поле 'status' в ответе"
        ad_id = extract_id_from_status(status_str)
    assert ad_id, "Не удалось извлечь id объявления"
    delete_resp = delete_item(ad_id)
    assert delete_resp.status_code == 200, f"Ожидаем 200, получен {delete_resp.status_code}"
    assert delete_resp.text == "", "Ожидаем пустое тело ответа после удаления"

def test_17_delete_nonexistent_item():
    """Удаление несуществующего объявления (DELETE /api/2/item/:id) -> 404 Not Found."""
    fake_id = "00000000-0000-0000-0000-000000000099"
    resp = delete_item(fake_id)
    assert resp.status_code == 404, f"Ожидаем 404, получен {resp.status_code}"
    data = resp.json()
    assert "result" in data, "Ожидаем поле 'result'"
    assert "status" in data, "Ожидаем поле 'status'"
