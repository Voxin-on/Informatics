import sqlite3

connection = sqlite3.connect("baza.db")
cursor = connection.cursor()

sql_script = """
CREATE TABLE IF NOT EXISTS education_levels (
    id_level INTEGER PRIMARY KEY NOT NULL UNIQUE,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS majors (
    id_major INTEGER PRIMARY KEY NOT NULL UNIQUE,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS study_types (
    id_type INTEGER PRIMARY KEY NOT NULL UNIQUE,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS students (
    id_student INTEGER PRIMARY KEY NOT NULL UNIQUE,
    id_level INTEGER,
    id_major INTEGER,
    id_type INTEGER,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    middle_name TEXT,
    gpa INTEGER CHECK(gpa >= 0 AND gpa <= 5),
    FOREIGN KEY (id_level) REFERENCES education_levels(id_level),
    FOREIGN KEY (id_major) REFERENCES majors(id_major),
    FOREIGN KEY (id_type) REFERENCES study_types(id_type)
);
"""
cursor.executescript(sql_script)


levels = []
with open("level_education.txt", 'r', encoding='utf-8') as file:
    for line in file:
        data = line.strip().split(';')
        levels.append(tuple(data))

cursor.executemany("""
    INSERT OR IGNORE INTO education_levels (id_level, name)
    VALUES (?, ?)
""", levels)

types = []
with open("type_education.txt", 'r', encoding='utf-8') as file:
    for line in file:
        data = line.strip().split(';')
        types.append(tuple(data))

cursor.executemany("""
    INSERT OR IGNORE INTO study_types (id_type, name)
    VALUES (?, ?)
""", types)

majors = []
with open("major.txt", 'r', encoding='utf-8') as file:
    for line in file:
        data = line.strip().split(';')
        majors.append(tuple(data))

cursor.executemany("""
    INSERT OR IGNORE INTO majors (id_major, name)
    VALUES (?, ?)
""", majors)

students = []
with open("students.txt", 'r', encoding='utf-8') as file:
    for line in file:
        data = line.strip().split(';')
        students.append(tuple(data))

cursor.executemany("""
    INSERT OR IGNORE INTO students (id_student, id_level, id_major, id_type, last_name, first_name, middle_name, gpa)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", students)

connection.commit()


 
#SQL запросы Case подзапросы CTE
print("\nSQL запросы Case подзапросы CTE")
cursor.execute("""
    SELECT last_name, first_name, gpa,
    CASE
        WHEN gpa =5 THEN 'ОТЛИЧНИК'
        WHEN gpa >=4 then 'ХОРОШИСТ'
        WHEN gpa >=3 then 'ТРОЕЧНИК'
        ELSE 'НЕУСПЕВАЮЩИЙ'
    END as grade_group
    FROM students           
""") 

rows = cursor.fetchall()
print("\nКатегории успеваемости:")
for row in rows:
    print(f"{row[0]} {row[1]}: {row[2]} — {row[3]}")
    
cursor.execute("""
    SELECT last_name, first_name, st.name,
    CASE
        WHEN st.name ='Очная' THEN 'Посещает занятия в вузе'
        WHEN st.name ='Заочная' then 'Учиться дома самостоятельно'
        WHEN st.name ='Вечерняя' then 'Посещает занятия в вузе вечером'
        ELSE 'Неизвестная форма'
    END as full_meaning
    FROM students s
    JOIN study_types st ON s.id_type = st.id_type        
""") 

cursor.execute("""
    SELECT last_name, first_name, el.name,
    CASE
        WHEN el.name = 'Бакалавриат' THEN 'Базовый уровень'
        WHEN el.name = 'Магистратура' THEN 'Продвинутый уровень'
        WHEN el.name = 'Аспирантура' THEN 'Исследовательский уровень'
        ELSE 'Прочее'
    END AS уровень_подготовки
    FROM students s
    JOIN education_levels el ON s.id_level = el.id_level
""")

rows = cursor.fetchall()
print("\nУровень подготовки:")
for row in rows:
    print(f"  {row[0]} {row[1]} ({row[2]}): {row[3]}")

rows = cursor.fetchall()
print("\nЗначение форм обучений:")
for row in rows:
    print(f"{row[0]} {row[1]}: {row[2]} — {row[3]}")
    
cursor.execute("""
    SELECT last_name, first_name, gpa
    FROM students
    WHERE gpa>(SELECT AVG(gpa) FROM students)      
""") 

rows = cursor.fetchall()
print("\nСтуденты с баллом выше среднего:")
for row in rows:
    print(f"{row[0]} {row[1]}: {row[2]}")
    
cursor.execute("""
    SELECT last_name, first_name, gpa 
    FROM students
    WHERE gpa=(SELECT MAX(gpa) FROM students)     
""")

rows = cursor.fetchall()
print("\nСтуденты с максимальным баллом:")
for row in rows:
    print(f"{row[0]} {row[1]}: {row[2]}")
    
cursor.execute("""
    SELECT m.name, ROUND(AVG(s.gpa), 2) AS avg_gpa
    FROM students s
    JOIN majors m ON s.id_major = m.id_major
    GROUP BY m.id_major
    HAVING AVG(s.gpa)>(SELECT AVG(gpa) FROM students)  
""")

rows = cursor.fetchall()
print("\nНаправление где средний балл выше обшего:")
for row in rows:
    print(f"{row[0]} {row[1]}")
    
cursor.execute("""
    WITH avg_by_major AS (
        SELECT id_major, ROUND(AVG(gpa), 2) AS avg_gpa
        FROM students
        GROUP BY id_major
    )
    SELECT m.name, a.avg_gpa
    FROM avg_by_major a
    JOIN majors m ON a.id_major = m.id_major
    ORDER BY a.avg_gpa DESC
""")
rows = cursor.fetchall()
print("\nСредний балл по направлениям:")
for row in rows:
    print(f"  {row[0]}: {row[1]}")

cursor.execute("""
    WITH overall_avg AS (
        SELECT ROUND(AVG(gpa), 2) AS avg_gpa
        FROM students
    )
    SELECT s.last_name, s.first_name, s.gpa, o.avg_gpa
    FROM students s, overall_avg o
    WHERE s.gpa > o.avg_gpa
    ORDER BY s.gpa DESC
""")
rows = cursor.fetchall()
print("\nСтуденты с баллом выше среднего:")
for row in rows:
    print(f"  {row[0]} {row[1]}: {row[2]} (средний по всем: {row[3]})")

connection.close()