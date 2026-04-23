
## Тексты SQL-запросов

### 1 Создание чека

```sql
INSERT INTO receipts (created_at, id_cashier)
VALUES ('2026-04-23 14:32:00', 1);
```

### 2 Добавление товара в чек

```sql
INSERT INTO sale_items (id_check, id_product, quantity)
VALUES (1, 2, 3.0);
```

### 3 Списание товара со склада после продажи

```sql
UPDATE products
SET quantity_at_storage = quantity_at_storage - 3.0
WHERE id_product = 2;
```

### 4 Проверка остатка перед продажей

```sql
SELECT quantity_at_storage
FROM products
WHERE name = 'Молоко';
```

### 5 Отчёт за выбранную дату — количество и выручка по каждому товару

```sql
SELECT
    p.name,
    SUM(si.quantity)             AS количество,
    SUM(si.quantity * p.price)   AS выручка
FROM sale_items si
JOIN products p ON si.id_product = p.id_product
JOIN receipts r ON si.id_check = r.id_check
WHERE DATE(r.created_at) = '2026-04-23'
GROUP BY p.name;
```

### 6 Добавление нового товара на склад

```sql
INSERT INTO products (name, price, id_category, quantity_at_storage)
VALUES ('Кефир', 65.50, 1, 40);
```

### 7 Пополнение остатка существующего товара

```sql
UPDATE products
SET quantity_at_storage = quantity_at_storage + 20
WHERE name = 'Хлеб';
```
