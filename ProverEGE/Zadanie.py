import sqlite3
import pandas as pd

file = '3.xls'

df_shops = pd.read_excel(file, sheet_name='Магазин')
df_products = pd.read_excel(file, sheet_name='Товар')
df_trans = pd.read_excel(file, sheet_name='Движение товаров')

df_trans['Дата'] = pd.to_datetime(df_trans['Дата']).dt.strftime('%Y-%m-%d')


conn = sqlite3.connect(':memory:')
df_shops.to_sql('Shops', conn, index=False)
df_products.to_sql('Products', conn, index=False)
df_trans.to_sql('Transactions', conn, index=False)

cursor = conn.cursor()

query = """
SELECT 
    SUM(t."Количество упаковок, шт" * p."Цена за упаковку") 
FROM 
    Transactions t
JOIN 
    Products p ON t."Артикул" = p."Артикул"
JOIN 
    Shops s ON t."ID магазина" = s."ID магазина"
WHERE 
    s."Район" = 'Нагорный'
    -- Фильтр LIKE 'Молоко%' найдет всё, что начинается с этого слова
    AND p."Наименование товара" LIKE 'Молоко ультрапастеризованное%'
    AND t."Тип операции" = 'Поступление'
    -- Даты теперь в строгом формате ГГГГ-ММ-ДД
    AND t."Дата" >= '2024-10-02' 
    AND t."Дата" <= '2024-10-09';
"""

cursor.execute(query)
total = cursor.fetchone()[0]

print(f"Итоговый результат: {total}")
conn.close()