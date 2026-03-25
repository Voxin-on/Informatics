import sqlite3

connection = sqlite3.connect("baza.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS `job_titles` (
        `id_job_title` INTEGER PRIMARY KEY NOT NULL UNIQUE,
        `name` TEXT NOT NULL
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS `employees` (
        `id` INTEGER PRIMARY KEY NOT NULL UNIQUE,
        `surname` TEXT NOT NULL,
        `name` TEXT NOT NULL,
        `phone_number` TEXT NOT NULL,
        `id_job_title` INTEGER NOT NULL,
        FOREIGN KEY ('id_job_title') REFERENCES `job_titles`('id_job_title')
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS `clients` (
        `id` INTEGER PRIMARY KEY NOT NULL UNIQUE,
        `Organization` TEXT NOT NULL,
        `phone_number` TEXT NOT NULL
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS `orders` (
        `id_order` INTEGER PRIMARY KEY NOT NULL UNIQUE,
        `id_client` INTEGER NOT NULL,
        `id_employ` INTEGER NOT NULL,
        `sum` INTEGER NOT NULL,
        `date_completion` TEXT NOT NULL,
        `mark_completion` INTEGER NOT NULL,
        FOREIGN KEY (`id_client`) REFERENCES `clients`(`id`),
        FOREIGN KEY ('id_employ') REFERENCES `employees`('id')
    );
""")

job_titles_data = [
    (1, "Менеджер"),
    (2, "Разработчик"),
    (3, "Аналитик"),
    (4, "Дизайнер"),
]
cursor.executemany("INSERT OR IGNORE INTO `job_titles` (`id_job_title`, `name`) VALUES (?, ?)", job_titles_data)

employees_data = [
    (1, "Иванов", "Иван", "+7-900-111-00-01", 2),
    (2, "Петров", "Алексей", "+7-900-111-00-02", 1),
    (3, "Сидорова", "Марина", "+7-900-111-00-03", 3),
    (4, "Кузнецов", "Дмитрий", "+7-900-111-00-04", 2),
    (5, "Смирнова", "Елена", "+7-900-111-00-05", 4),
    (6, "Попов", "Андрей", "+7-900-111-00-06", 2),
    (7, "Васильев", "Сергей", "+7-900-111-00-07", 1),
    (8, "Павлова", "Ольга", "+7-900-111-00-08", 3),
    (9, "Соколов", "Игорь", "+7-900-111-00-09", 2),
    (10, "Михайлов", "Артем", "+7-900-111-00-10", 4),
]
 
cursor.executemany(
    "INSERT OR IGNORE INTO `employees` (`id`, `surname`, `name`, `phone_number`, `id_job_title`) VALUES (?, ?, ?, ?, ?)",
    employees_data
)

clients_data = [
    (1, "ООО 'ТехноМир'", "8-800-555-01-01"),
    (2, "ИП Соколов", "8-800-555-01-02"),
    (3, "ПАО 'ГазПромСтрой'", "8-800-555-01-03"),
    (4, "Магазин 'Уют'", "8-800-555-01-04"),
    (5, "Кафе 'Рассвет'", "8-800-555-01-05"),
]
cursor.executemany(
    "INSERT OR IGNORE INTO `clients` (`id`, `Organization`, `phone_number`) VALUES (?, ?, ?)",
    clients_data
)

orders_data = [
    (101, 1, 2, 50000, "2023-10-25", 1),
    (102, 2, 4, 15000, "2023-11-01", 0),
    (103, 3, 1, 120000, "2023-10-20", 1),
    (104, 4, 6, 8500, "2023-11-05", 0),
    (105, 5, 2, 32000, "2023-10-28", 1),
]
cursor.executemany(
    "INSERT OR IGNORE INTO `orders` (`id_order`, `id_client`, `id_employ`, `sum`, `date_completion`, `mark_completion`) VALUES (?, ?, ?, ?, ?, ?)",
    orders_data
)

connection.commit()

#Простые
cursor.execute("SELECT COUNT(*) FROM employees")
print("Количество сотрудников:", cursor.fetchone()[0])

cursor.execute("SELECT MAX(sum) FROM orders")
print("Максимальная сумма заказа:", cursor.fetchone()[0])

cursor.execute("SELECT MIN(sum) FROM orders")
print("Минимальная сумма заказа:", cursor.fetchone()[0])

cursor.execute("SELECT SUM(sum) FROM orders")
print("Общая сумма заказов:", cursor.fetchone()[0])

cursor.execute("SELECT AVG(sum) FROM orders")
print("Средняя сумма заказа:", cursor.fetchone()[0])


#С агрегацией
cursor.execute("""
    SELECT c.Organization, COUNT(o.id_order) AS количество_заказов
    FROM clients c
    JOIN orders o ON c.id = o.id_client
    GROUP BY c.id
""")
orders_by_client = cursor.fetchall()
print("Количество заказов у каждого клиента")
for row in orders_by_client:
    print(f"{row[0]} — {row[1]} заказов")
    
cursor.execute("""
    SELECT e.surname, e.name, SUM(o.sum) AS общая_сумма
    FROM employees e
    JOIN orders o ON e.id = o.id_employ
    GROUP BY e.id
""")
sum_by_employee = cursor.fetchall()
print("\nОбщая сумма заказов по каждому сотруднику")
for row in sum_by_employee:
    print(f"{row[0]} {row[1]} — {row[2]} руб.")
    
cursor.execute("""
    SELECT j.name, AVG(o.sum) AS средняя_сумма
    FROM job_titles j
    JOIN employees e ON j.id_job_title = e.id_job_title
    JOIN orders o ON e.id = o.id_employ
    GROUP BY j.id_job_title
""")
avg_by_job = cursor.fetchall()
print("\nСредняя сумма заказов по должностям")
for row in avg_by_job:
    print(f"{row[0]} — {row[1]:.2f} руб.")

#С объединением и условиями
cursor.execute("""
    SELECT c.Organization, e.surname, e.name, o.sum, o.date_completion
    FROM orders o
    JOIN clients c ON o.id_client = c.id
    JOIN employees e ON o.id_employ = e.id
    WHERE o.mark_completion = 1
""")
completed_orders = cursor.fetchall()
print("Завершённые заказы")
for row in completed_orders:
    print(f"{row[0]} — {row[1]} {row[2]}, сумма: {row[3]} руб., дата: {row[4]}")

cursor.execute("""
    SELECT e.surname, e.name, o.sum, o.date_completion
    FROM employees e
    JOIN job_titles j ON e.id_job_title = j.id_job_title
    JOIN orders o ON e.id = o.id_employ
    WHERE j.name = 'Разработчик'
""")
dev_orders = cursor.fetchall()
print("\nЗаказы разработчиков")
for row in dev_orders:
    print(f"{row[0]} {row[1]} — {row[2]} руб., дата: {row[3]}")

cursor.execute("""
    SELECT c.Organization, SUM(o.sum) AS общая_сумма
    FROM clients c
    JOIN orders o ON c.id = o.id_client
    GROUP BY c.id
    HAVING SUM(o.sum) > 20000
""")
big_clients = cursor.fetchall()
print("\nКлиенты с общей суммой заказов больше 20000 руб.")
for row in big_clients:
    print(f"{row[0]} — {row[1]} руб.")


connection.close()