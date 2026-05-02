import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

def init_db():
    with sqlite3.connect("baza.db") as connection:
        cursor = connection.cursor()
        
        sql_script = """
        CREATE TABLE IF NOT EXISTS `categories` (
            `id_category` INTEGER PRIMARY KEY AUTOINCREMENT,
            `name_category` TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS `products` (
            `id_product` INTEGER PRIMARY KEY AUTOINCREMENT,
            `name` TEXT NOT NULL,
            `price` REAL NOT NULL,
            `id_category` INTEGER NOT NULL,
            `quantity_at_storage` REAL NOT NULL,
            FOREIGN KEY(`id_category`) REFERENCES `categories`(`id_category`)
        );

        CREATE TABLE IF NOT EXISTS `jobs_titles` (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `name` TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS `employees` (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `name` TEXT NOT NULL,
            `surname` TEXT NOT NULL,
            `id_job_title` INTEGER NOT NULL,
            FOREIGN KEY(`id_job_title`) REFERENCES `jobs_titles`(`id`)
        );

        CREATE TABLE IF NOT EXISTS `receipts` (
            `id_check` INTEGER PRIMARY KEY AUTOINCREMENT,
            `created_at` DATETIME NOT NULL,
            `id_cashier` INTEGER NOT NULL,
            FOREIGN KEY(`id_cashier`) REFERENCES `employees`(`id`)
        );

        CREATE TABLE IF NOT EXISTS `sale_items` (
            `id_sale` INTEGER PRIMARY KEY AUTOINCREMENT,
            `id_check` INTEGER NOT NULL,
            `id_product` INTEGER NOT NULL,
            `quantity` REAL NOT NULL,
            FOREIGN KEY(`id_check`) REFERENCES `receipts`(`id_check`),
            FOREIGN KEY(`id_product`) REFERENCES `products`(`id_product`)
        );
        """
        cursor.executescript(sql_script)

        cursor.execute("SELECT COUNT(*) FROM employees")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO jobs_titles (name) VALUES ('Администратор')")
            cursor.execute("INSERT INTO employees (name, surname, id_job_title) VALUES ('Система', 'Главная', 1)")
            
        connection.commit()

class ShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Магазин")
        self.root.geometry("650x550")
        
        self.conn = sqlite3.connect("baza.db")
        self.cursor = self.conn.cursor()
        
        self.cart = []
        self.create_widgets()

    def create_widgets(self):
        tabs = ttk.Notebook(self.root)
        
        # Чек
        sale_tab = ttk.Frame(tabs)
        tabs.add(sale_tab, text="Оформление продажи")
        
        tk.Label(sale_tab, text="Товар:").pack(pady=5)
        self.product_cb = ttk.Combobox(sale_tab, values=self.get_product_names(), state="readonly")
        self.product_cb.pack()
        
        tk.Label(sale_tab, text="Количество:").pack(pady=5)
        self.qty_entry = tk.Entry(sale_tab)
        self.qty_entry.pack()
        
        tk.Button(sale_tab, text="Добавить в чек", command=self.add_to_cart, bg="#e1f5fe").pack(pady=10)
        
        self.cart_list = tk.Listbox(sale_tab, width=60, height=10)
        self.cart_list.pack(pady=5)
        
        tk.Button(sale_tab, text="ЗАВЕРШИТЬ ПОКУПКУ", command=self.finish_sale, bg="#ffcc80", font=("Arial", 10, "bold")).pack(pady=10)

        tk.Label(sale_tab, text="Выберите кассира:", font=("Arial", 10, "bold")).pack(pady=5)

        self.employees_map = self.get_employees_map()
        self.cashier_cb = ttk.Combobox(sale_tab, values=list(self.employees_map.keys()), state="readonly", width=30)
        self.cashier_cb.pack(pady=5)
        if self.employees_map:
            self.cashier_cb.current(0)

        # Отчёты
        report_tab = ttk.Frame(tabs)
        tabs.add(report_tab, text="Отчеты")
        
        report_top = tk.Frame(report_tab)
        report_top.pack(pady=10)
        
        tk.Label(report_top, text="Выберите дату:").pack(side=tk.LEFT, padx=5)
        self.cal = DateEntry(report_top, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.cal.pack(side=tk.LEFT, padx=5)
        
        tk.Button(report_tab, text="Сформировать отчет", command=self.show_report).pack(pady=5)
        
        self.report_text = tk.Text(report_tab, height=15, width=70)
        self.report_text.pack(pady=10, padx=10)

        # Склад добавление
        goods_tab = ttk.Frame(tabs)
        tabs.add(goods_tab, text="Склад")

        tk.Label(goods_tab, text="Название:").pack(pady=5)
        self.new_name = tk.Entry(goods_tab, width=30)
        self.new_name.pack()

        tk.Label(goods_tab, text="Цена:").pack(pady=5)
        self.new_price = tk.Entry(goods_tab, width=30)
        self.new_price.pack()

        tk.Label(goods_tab, text="Количество на складе:").pack(pady=5)
        self.new_stock = tk.Entry(goods_tab, width=30)
        self.new_stock.pack()

        tk.Label(goods_tab, text="Категория:").pack(pady=5)
        self.cursor.execute("SELECT id_category, name_category FROM categories")
        cats = self.cursor.fetchall()
        self.cat_map = {c[1]: c[0] for c in cats}
        self.new_cat = ttk.Combobox(goods_tab, values=list(self.cat_map.keys()), width=28)
        self.new_cat.pack()

        tk.Button(goods_tab, text="Добавить товар", command=self.add_product, bg="#c8e6c9", font=("Arial", 10, "bold")).pack(pady=15)

        # удаление
        tk.Frame(goods_tab, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=10)
        
        tk.Label(goods_tab, text="Списание товара (корректировка остатков):", font=("Arial", 10, "bold")).pack()

        write_off_frame = tk.Frame(goods_tab) 
        write_off_frame.pack(pady=5)
        
        self.delete_cb = ttk.Combobox(write_off_frame, values=self.get_product_names(), state="readonly", width=25)
        self.delete_cb.pack(side=tk.LEFT, padx=5)
        
        tk.Label(write_off_frame, text="Кол-во:").pack(side=tk.LEFT)
        self.write_off_qty = tk.Entry(write_off_frame, width=10)
        self.write_off_qty.pack(side=tk.LEFT, padx=5)

        tk.Button(write_off_frame, text="СПИСАТЬ", command=self.write_off_product, bg="#ffcdd2").pack(side=tk.LEFT, padx=5)

        tabs.pack(expand=1, fill="both")

        # сотрудники
        empl_tab = ttk.Frame(tabs)
        tabs.add(empl_tab, text="Сотрудники")

        tk.Label(empl_tab, text="Имя:", font=("Arial", 10)).pack(pady=5)
        self.emp_name = tk.Entry(empl_tab, width=30)
        self.emp_name.pack()

        tk.Label(empl_tab, text="Фамилия:", font=("Arial", 10)).pack(pady=5)
        self.emp_surname = tk.Entry(empl_tab, width=30)
        self.emp_surname.pack()

        tk.Label(empl_tab, text="Должность:", font=("Arial", 10)).pack(pady=5)
        
        self.cursor.execute("SELECT id, name FROM jobs_titles")
        jobs = self.cursor.fetchall()
        self.job_map = {j[1]: j[0] for j in jobs}
        
        self.emp_job_cb = ttk.Combobox(empl_tab, values=list(self.job_map.keys()), width=28)
        self.emp_job_cb.pack()

        tk.Button(empl_tab, text="Добавить сотрудника", command=self.add_employee, bg="#bbdefb", font=("Arial", 10, "bold")).pack(pady=20)

        self.emp_list = tk.Listbox(empl_tab, width=50, height=8)
        self.emp_list.pack(pady=10)
        self.refresh_employee_list()

    def add_product(self):
        name  = self.new_name.get().strip()
        cat_input = self.new_cat.get().strip()

        if not name or not cat_input:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        try:
            price = float(self.new_price.get().replace(",", "."))
            stock = float(self.new_stock.get().replace(",", "."))
            if price <= 0 or stock < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Цена и количество должны быть числами!")
            return

        if cat_input in self.cat_map:
            cat_id = self.cat_map[cat_input]
        else:
            confirm_cat = messagebox.askyesno("Новая категория", 
                f"Категории «{cat_input}» не существует. Создать её?")
            if not confirm_cat: return
            
            self.cursor.execute("INSERT INTO categories (name_category) VALUES (?)", (cat_input,))
            self.conn.commit()
            cat_id = self.cursor.lastrowid

            self.cursor.execute("SELECT id_category, name_category FROM categories")
            cats = self.cursor.fetchall()
            self.cat_map = {c[1]: c[0] for c in cats}
            self.new_cat["values"] = list(self.cat_map.keys())

        self.cursor.execute("SELECT id_product, quantity_at_storage, price FROM products WHERE name = ?", (name,))
        existing_product = self.cursor.fetchone()

        if existing_product:
            p_id, current_qty, old_price = existing_product
            new_qty = current_qty + stock
            if abs(old_price - price) < 0.001 or messagebox.askyesno("Изменение цены", f"Обновить цену для «{name}»?"):
                self.cursor.execute("UPDATE products SET price=?, quantity_at_storage=?, id_category=? WHERE id_product=?",
                                   (price, new_qty, cat_id, p_id))
        else:
            self.cursor.execute("INSERT INTO products (name, price, id_category, quantity_at_storage) VALUES (?,?,?,?)",
                               (name, price, cat_id, stock))
        
        self.conn.commit()
        messagebox.showinfo("Готово", "Данные в базе обновлены")

        updated_list = self.get_product_names()
        self.product_cb["values"] = updated_list
        self.delete_cb["values"] = updated_list

        self.new_name.delete(0, tk.END)
        self.new_price.delete(0, tk.END)
        self.new_stock.delete(0, tk.END)
        self.new_cat.set('')

    def write_off_product(self):
        name = self.delete_cb.get()
        qty_str = self.write_off_qty.get().replace(",", ".")

        if not name or not qty_str:
            messagebox.showwarning("Ошибка", "Выберите товар и введите количество!")
            return

        try:
            qty_to_remove = float(qty_str)
            if qty_to_remove <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите положительное число!")
            return

        self.cursor.execute("SELECT quantity_at_storage FROM products WHERE name = ?", (name,))
        res = self.cursor.fetchone()
        
        if res:
            current_stock = res[0]
            if qty_to_remove > current_stock:
                if not messagebox.askyesno("Внимание", f"На складе всего {current_stock}. Списать всё в ноль?"):
                    return
                qty_to_remove = current_stock

            new_stock = current_stock - qty_to_remove

            self.cursor.execute("UPDATE products SET quantity_at_storage = ? WHERE name = ?", (new_stock, name))
            self.conn.commit()
            
            messagebox.showinfo("Готово", f"Списано {qty_to_remove} шт. Остаток товара «{name}»: {new_stock} шт.")

            self.write_off_qty.delete(0, tk.END)

    def add_employee(self):
        name = self.emp_name.get().strip()
        surname = self.emp_surname.get().strip()
        job_input = self.emp_job_cb.get().strip()

        if not all([name, surname, job_input]):
            messagebox.showwarning("Ошибка", "Заполните все данные сотрудника!")
            return


        if job_input in self.job_map:
            job_id = self.job_map[job_input]
        else:
            if not messagebox.askyesno("Новая должность", f"Должности «{job_input}» нет. Создать?"):
                return
            
            self.cursor.execute("INSERT INTO jobs_titles (name) VALUES (?)", (job_input,))
            self.conn.commit()
            job_id = self.cursor.lastrowid

            self.job_map[job_input] = job_id
            self.emp_job_cb["values"] = list(self.job_map.keys())

        self.cursor.execute(
            "INSERT INTO employees (name, surname, id_job_title) VALUES (?, ?, ?)",
            (name, surname, job_id)
        )
        self.conn.commit()
        
        messagebox.showinfo("Успех", f"Сотрудник {name} {surname} добавлен!")

        self.emp_name.delete(0, tk.END)
        self.emp_surname.delete(0, tk.END)
        self.emp_job_cb.set('')
        self.refresh_employee_list()

        self.employees_map = self.get_employees_map()
        self.cashier_cb["values"] = list(self.employees_map.keys())

    def refresh_employee_list(self):
        self.emp_list.delete(0, tk.END)
        self.cursor.execute("""
            SELECT e.name, e.surname, j.name 
            FROM employees e 
            JOIN jobs_titles j ON e.id_job_title = j.id
        """)
        for row in self.cursor.fetchall():
            self.emp_list.insert(tk.END, f"{row[0]} {row[1]} — {row[2]}")

    def get_product_names(self):
        self.cursor.execute("SELECT name FROM products")
        return [row[0] for row in self.cursor.fetchall()]

    def add_to_cart(self):
        name = self.product_cb.get()
        if not name: return
        
        try:
            qty = float(self.qty_entry.get())
            if qty <= 0:
                messagebox.showerror("Ошибка", "Количество должно быть больше нуля!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите число!")
            return

        self.cursor.execute("SELECT id_product, price, quantity_at_storage FROM products WHERE name=?", (name,))
        p_id, price, stock = self.cursor.fetchone()

        already_in_cart = sum(i['qty'] for i in self.cart if i['id'] == p_id)

        if already_in_cart + qty > stock:
            messagebox.showwarning("Склад", f"Недостаточно! В наличии: {stock}, уже в корзине: {already_in_cart}")
            return

        for item in self.cart:
            if item['id'] == p_id:
                item['qty'] += qty
                idx = self.cart.index(item)
                self.cart_list.delete(idx)
                self.cart_list.insert(idx, f"{name} | {item['qty']} шт. | {item['qty']*price} руб.")
                return

        self.cart.append({'id': p_id, 'name': name, 'qty': qty, 'price': price})
        self.cart_list.insert(tk.END, f"{name} | {qty} шт. | {qty*price} руб.")

    def get_employees_map(self):
        self.cursor.execute("SELECT id, name, surname FROM employees")
        return {f"{row[1]} {row[2]}": row[0] for row in self.cursor.fetchall()}

    def finish_sale(self):
        if not self.cart: 
            messagebox.showwarning("Ошибка", "Корзина пуста!")
            return
            
        cashier_name = self.cashier_cb.get()
        if not cashier_name:
            messagebox.showwarning("Ошибка", "Выберите кассира!")
            return
            
        cashier_id = self.employees_map[cashier_name]
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Используем cashier_id вместо 1
        self.cursor.execute("INSERT INTO receipts (created_at, id_cashier) VALUES (?, ?)", (now, cashier_id))
        check_id = self.cursor.lastrowid
        
        for item in self.cart:
            self.cursor.execute("INSERT INTO sale_items (id_check, id_product, quantity) VALUES (?,?,?)",
                               (check_id, item['id'], item['qty']))
            self.cursor.execute("UPDATE products SET quantity_at_storage = quantity_at_storage - ? WHERE id_product = ?",
                               (item['qty'], item['id']))
            
        self.conn.commit()
        messagebox.showinfo("Успех", f"Чек №{check_id} оформлен кассиром {cashier_name}!")
        self.cart = []
        self.cart_list.delete(0, tk.END)

    def show_report(self):
        selected_date = self.cal.get_date().strftime("%Y-%m-%d")
        
        query = """
            SELECT p.name, SUM(si.quantity), SUM(si.quantity * p.price)
            FROM sale_items si
            JOIN products p ON si.id_product = p.id_product
            JOIN receipts r ON si.id_check = r.id_check
            WHERE DATE(r.created_at) = ?
            GROUP BY p.name
        """
        self.cursor.execute(query, (selected_date,))
        rows = self.cursor.fetchall()
        
        self.report_text.delete('1.0', tk.END)
        self.report_text.insert(tk.END, f"ОТЧЕТ ЗА {selected_date}\n" + "="*40 + "\n")
        
        total_day = 0
        for name, q, summ in rows:
            self.report_text.insert(tk.END, f"{name:20} | {q:5} шт. | {summ:8} руб.\n")
            total_day += summ
        self.report_text.insert(tk.END, "="*40 + f"\nИТОГО ЗА ДЕНЬ: {total_day} руб.")

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = ShopApp(root)
    root.mainloop()