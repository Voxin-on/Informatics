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
    gpa INTEGER,
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


cursor.execute("SELECT COUNT(*) FROM students")
total = cursor.fetchone()[0]
print(f"Всего студентов: {total}")


cursor.execute("""
    SELECT m.name, COUNT(s.id_student) AS count
    FROM majors m
    LEFT JOIN students s ON m.id_major = s.id_major
    GROUP BY m.id_major, m.name
    ORDER BY count DESC
""")
rows = cursor.fetchall()
print("\nКоличество студентов по направлениям:")
for row in rows:
    print(f"  {row[0]}: {row[1]}")


cursor.execute("""
    SELECT st.name, COUNT(s.id_student) AS count
    FROM study_types st
    LEFT JOIN students s ON st.id_type = s.id_type
    GROUP BY st.id_type, st.name
    ORDER BY count DESC
""")
rows = cursor.fetchall()
print("\nКоличество студентов по формам обучения:")
for row in rows:
    print(f"  {row[0]}: {row[1]}")


cursor.execute("""
    SELECT m.name,
           MAX(s.gpa) AS max_gpa,
           MIN(s.gpa) AS min_gpa,
           ROUND(AVG(s.gpa), 2) AS avg_gpa
    FROM majors m
    LEFT JOIN students s ON m.id_major = s.id_major
    GROUP BY m.id_major, m.name
    ORDER BY avg_gpa DESC
""")
rows = cursor.fetchall()
print("\nБаллы студентов по направлениям:")
for row in rows:
    print(f"  {row[0]}: макс={row[1]}, мин={row[2]}, средний={row[3]}")


cursor.execute("""
    SELECT m.name, el.name, st.name,
           ROUND(AVG(s.gpa), 2) AS avg_gpa
    FROM students s
    JOIN majors m ON s.id_major = m.id_major
    JOIN education_levels el ON s.id_level = el.id_level
    JOIN study_types st ON s.id_type = st.id_type
    GROUP BY m.id_major, el.id_level, st.id_type
    ORDER BY m.name, el.name, st.name
""")
rows = cursor.fetchall()
print("\nСредний балл по направлениям, уровням и формам обучения:")
for row in rows:
    print(f"  {row[0]} | {row[1]} | {row[2]}: {row[3]}")


cursor.execute("""
    SELECT s.last_name, s.first_name, s.middle_name,
           m.name, el.name, st.name, s.gpa
    FROM students s
    JOIN majors m ON s.id_major = m.id_major
    JOIN education_levels el ON s.id_level = el.id_level
    JOIN study_types st ON s.id_type = st.id_type
    WHERE m.name = 'Прикладная Информатика'
      AND st.name = 'Очная'
    ORDER BY s.gpa DESC
    LIMIT 5
""")
rows = cursor.fetchall()
print("\nТоп-5 студентов для повышенной стипендии (Прикладная Информатика, Очная):")
print(f"  {'ФИО'} {'Направление'} {'Уровень'} {'Форма'} {'Балл'}")
for row in rows:
    fio = f"{row[0]} {row[1]} {row[2]}"
    print(f"  {fio} {row[3]} {row[4]} {row[5]} {row[6]}")

cursor.execute("""
    SELECT last_name, COUNT(*) AS count
    FROM students
    GROUP BY last_name
    HAVING COUNT(*) > 1
    ORDER BY count DESC
""")
rows = cursor.fetchall()
print("\nОднофамильцы:")
for row in rows:
    print(f"  {row[0]}: {row[1]} человека(ек)")

cursor.execute("""
    SELECT last_name, first_name, middle_name, COUNT(*) AS count
    FROM students
    GROUP BY last_name, first_name, middle_name
    HAVING COUNT(*) > 1
    ORDER BY count DESC
""")
rows = cursor.fetchall()
print("\nПолные тёзки:")
for row in rows:
    print(f"  {row[0]} {row[1]} {row[2]}: {row[3]} человека(ек)")
    
connection.close()