import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()


cur.execute("INSERT INTO recipes (title, url, tags, ingredients, recipe) VALUES (?, ?, ?, ?, ?)",
            ('Тесто 28 см', 'tyesto-28-sm', '[dinner, supper]', '{milk: 10, eggs: 3}', 'Eat, cook')
            )

connection.commit()
connection.close()
