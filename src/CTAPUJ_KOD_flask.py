from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
import mysql.connector
import MySQLdb as mdb
from create_urls import do_url

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nJHu8sfVJkGULhsv8jkJ89kj'

dbconfig = {
    'host': '127.0.0.1',
    'user': 'recipesAdmin',
    'password': 'adminPASSWD',
    'database': 'mamarecipesDB'
}


def get_db_connection():
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()
    return conn, cursor


def get_post(name_id):
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()
    post = cursor.execute('SELECT * FROM recipres WHERE name = ', name_id).fetchone()
    conn.close()
    if post is None:
        abort(404)
    cursor.close()
    conn.close()
    return post


def create(name, tags, ingredients, recipe, url):
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()
    _SQL = """insert into reciptes
        (name, tags, ingredients, recipe, url)
        values
        (%s, %s , %s, %s, %s)"""
    cursor.execute(_SQL, (name, tags, ingredients, recipe, url))
    conn.commit()
    _SQL = """select * from reciptes"""
    cursor.execute(_SQL)
    for row in cursor.fetchall():
        print(row)
    cursor.close()
    conn.close()


@app.route('/', methods=('GET', 'POST'))
def index():
    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()
    # conn.commit()
    cursor.execute('SELECT id FROM reciptes')
    recipes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", recipes=recipes)


@app.route('/kjk' + '<name_id>')
def post(name_id):
    recipe = get_post(name_id)
    return render_template('recipe.html', recipe=recipe)


@app.route('/create', methods=('GET', 'POST'))
def create():
    ingredient_list = {}
    i = 0
    if request.method == 'POST':
        name = request.form.get('name')
        url = do_url(name)
        while True:
            try:
                ingredient = request.form['ingredient' + str(i)]
                quantity = request.form['quantity' + str(i)]
                ingredient_list[ingredient] = quantity
                i += 1
            except KeyError:
                break
        ingredient_list = str(ingredient_list)
        tags = request.form.getlist('tag')
        tags = str(tags)
        recipe = request.form.get('recipe')
        create(name, ingredient_list, tags, recipe, url)
        if not name:
            flash('Name is required!')
        else:
            return redirect(url_for('index'))

    return render_template('create.html')


if __name__ == '__main__':
    app.run(debug=True, port=5002)
