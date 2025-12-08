# Документація тестування

## Запуск тестів

### Всі тести
```
pytest
```

### З покриттям коду
```
pytest --cov=. --cov-report=html
```

### Встановлення залежностей для тестів (локально)
```
pip install -r requirements-dev.txt
```

## Опис тестових сценаріїв

Тести організовані у каталозі `tests/` з підкаталогами `unit/` та `integration/`.

### Unit тести

#### TestModels.test_add_and_get_product
Перевіряє додавання продукту та його подальший пошук через `get_products`.

#### TestModels.test_update_and_delete_product
Перевіряє оновлення продукту та видалення.

#### TestModels.test_get_products_filters
Перевіряє фільтрацію по ціновому діапазону.

#### TestModels.test_get_products_has_image
Перевіряє фільтрацію по наявності зображення.

#### TestModels.test_add_order_empty_cart
Перевіряє створення замовлення з пустим кошиком; очікується успішне створення.

#### TestModels.test_get_orders_matching_email_partial_case
Перевіряє частковий та нечутливий до регістру пошук по email.

#### TestModels.test_get_order_details_items
Створює товар і замовлення з товаром, перевіряє наявність елементів у деталях замовлення.

#### TestModels.test_client_crud
Перевіряє CRUD для клієнтів (додавання, отримання).

#### TestModels.test_update_order_status_and_contact
Перевіряє оновлення статусу та контактів замовлення.

#### TestModels.test_get_products_invalid_price_filters
Перевіряє, що нечислові значення фільтрів ігноруються та не викликають помилок.

#### TestModels.test_add_order_malformed_cart_raises
Перевіряє негативний сценарій: некоректна структура кошика має призводити до помилки.

### Integration тести

#### TestAPIProducts
- test_create_product_api_success: перевіряє успішне створення продукту через API
- test_create_product_api_missing_fields: перевіряє валідацію тіла запиту
- test_get_products_api: перевіряє список продуктів через ендпоінт
- test_update_and_delete_product_api: повний цикл створення → оновлення → видалення

#### TestAPIOrders
- test_create_order_api: створення замовлення через API
- test_search_orders_api: пошук замовлень через `/orders/search` (частковий match)
- test_get_order_details_api: отримання деталей замовлення з елементами

#### TestAPIFeedback
- test_create_feedback_api: створення відгуку
- test_delete_feedback_api: видалення відгуку

#### TestDatabase
- test_init_db_creates_tables: перевіряє ініціалізацію таблиць

## Архітектура тестів і підходи
- Використано fixtures для налаштування тимчасової бази даних (`tests/conftest.py`).
- Тести організовано в класи відповідно до `pytest` рекомендацій (`Test*`).
- Використано принцип AAA (Arrange, Act, Assert) у кожному тесті.
- Є позитивні, негативні та граничні кейси.
- Setup/teardown: через fixtures `use_temp_db` та автозапуск `models.init_db()` для ізоляції середовища.

## CI/CD

Налаштовано GitHub Actions workflow: `.github/workflows/pytest.yml` — автоматичний запуск тестів при push/PR у `main`. Звіт про покриття зберігається як артефакт `coverage-report`.
