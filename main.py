from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort  # отображение ошибки
from werkzeug.utils import secure_filename  # проверка файла
import sqlite3
from create_urls import do_url
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nJHu8sfVJkGULhsv8jkJ89kj'

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Проверяет расштрение файла из доступных выше


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(url):
    conn = get_db_connection()
    content = conn.execute('SELECT * FROM recipes WHERE url = ?',
                        (url,)).fetchone()
    conn.close()
    if content is None:
        abort(404)
    return content


def get_post_title(title):
    conn = get_db_connection()
    content = conn.execute('SELECT * FROM recipes WHERE title = ?',
                        (title,)).fetchone()
    conn.close()
    if content is None:
        abort(404)
    return content


def get_tags_to_recipe(id):
    conn = get_db_connection()
    content = conn.execute("""SELECT * FROM tags
                                INNER JOIN tags_recipes ON recipes.id = tags_recipes.recipe
                                INNER JOIN tags ON tags_recipes.tag = tags.id
                                WHERE recipes.id=?""", (id,)).fetchall()
    conn.close()
    return content


def add_tag_to_tag_recipe(recipe_id, tags):
    conn = get_db_connection()
    _SQL = """insert into tags_recipes
            (recipe, tag)
            values
            (?, ?)"""
    lens = len(tags)
    for i in range(lens):
        print(tags[i])
        tag_id = conn.execute('SELECT id FROM tags WHERE title = ?',
                               (tags[i],)).fetchone()
        tag_id = tag_id['id']
        conn.execute(_SQL, (recipe_id, tag_id))
    conn.commit()
    conn.close()


def get_all_tags():
    conn = get_db_connection()
    content = conn.execute("SELECT * FROM tags").fetchall()
    conn.close()
    return content


def get_recipe_tag(title):
    conn = get_db_connection()
    content = conn.execute("""SELECT * FROM recipes
                                INNER JOIN tags_recipes ON recipes.id = tags_recipes.recipe
                                INNER JOIN tags ON tags_recipes.tag = tags.id
                                WHERE tags.id=?""", (title,)).fetchall()
    conn.close()
    return content


def create_recipe(title, url, tags, ingredients, recipe_content, image):
    conn = get_db_connection()
    _SQL = """insert into recipes
        (title, url, tags, ingredients, recipe, image)
        values
        (?, ?, ?, ?, ?, ?)"""
    conn.execute(_SQL, (title, url, tags, ingredients, recipe_content, image))
    conn.commit()
    conn.close()


def do_new_tag(tag_name):
    conn = get_db_connection()
    _SQL = """insert into tags
            (title)
            values
            (?)"""
    conn.execute(_SQL, (tag_name,))
    conn.commit()
    conn.close()


@app.route('/', methods=('POST', 'GET'))
def index():
    conn = get_db_connection()
    recipes = conn.execute('SELECT * FROM recipes').fetchall()
    conn.close()
    """id = recipes[0]['id']
    tags_content = get_tags_to_recipe(id)
    tag_list = []
    llo = 0
    print(tags_content)
    for i in tags_content:
        for t in i:
            llo += 1
            if llo == 12:
                tag_list.append(t)
        llo = 0"""
    all_tags = get_all_tags()
    return render_template("index.html", recipes=recipes, all_tags=all_tags)


@app.route('/<recipe_url>')
def recipe(recipe_url):
    recipe_content = get_post(str(recipe_url))
    tags = recipe_content['tags']
    tags = tags.split(',')
    print(tags)
    ingredients = recipe_content['ingredients']
    ingredients_dist = json.loads(ingredients)
    return render_template('recipe.html', tags=tags, recipe=recipe_content, ingredients=ingredients_dist)


@app.route('/<recipe_url>/edit', methods=('POST', 'GET'))
def edit(recipe_url):
    recipe_content = get_post(recipe_url)
    ingredients = recipe_content['ingredients']
    ingredients_dist = json.loads(ingredients)
    if request.method == 'POST':
        title = request.form['title']
        recipeC = request.form['recipe']
        if not title:
            flash('Требуется название!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE recipes SET title = ?, recipe = ?'
                         ' WHERE url = ?',
                         (title, recipeC, recipe_url))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    """all_tags = get_all_tags()
    recipe_tags = get_tags_to_recipe(recipe_content['id'])
    all_tags_list = []
    recipe_tags_list = []
    for i in all_tags:
        all_tags_list.append(i['title'])
    for i in recipe_tags:
        recipe_tags_list.append(i['title'])
    return render_template('edit.html', recipe=recipe_content, ingredients=ingredients_dist, tags=all_tags, recipe_tags=recipe_tags)"""
    return render_template('edit.html', recipe=recipe_content, ingredients=ingredients_dist)


@app.route('/<recipe_url>/delete', methods=['POST'])
def delete(recipe_url):
    recipe_content = get_post(recipe_url)
    conn = get_db_connection()
    conn.execute('DELETE FROM recipes WHERE url = ?', (recipe_url,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(recipe_content['title']))
    return redirect(url_for('index'))


@app.route('/create', methods=['POST', 'GET'])
def create():
    tags = get_all_tags()
    return render_template('create.html', tags=tags)


@app.route('/save', methods=['POST'])
def save():
    ingredient_list = ''
    i = 0
    if request.method == 'POST':
        title = request.form['title']
        recipe_url = do_url(title)
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = '../static/images/' + file.filename
        else:
            image_path = "../static/images/xleb.jpg"



        while True:
            try:
                ingredient = request.form['ingredient' + str(i)]
                quantity = request.form['quantity' + str(i)]
                ingredient_list += ('"' + ingredient + '": ' + '"' + quantity + '", ')
                i += 1
            except KeyError:
                break
        ingredient_list = '{' + ingredient_list[:-2] + '}'
        tags2 = ''
        tags = request.form.getlist('tag')
        for i in tags:
            tags2 += i
            tags2 += '|'
        tags2 = tags2[:-1]
        recipe_content = request.form['recipe']
        create_recipe(title, recipe_url, tags2, ingredient_list, recipe_content, image_path)

        recipe_content = get_post(recipe_url)
        recipe_id = recipe_content['id']
        add_tag_to_tag_recipe(recipe_id, tags)
    return redirect(url_for('index'))

"""CREATE TABLE recipes (
    id          INTEGER       PRIMARY KEY AUTOINCREMENT,
    created     TIMESTAMP     NOT NULL
                              DEFAULT CURRENT_TIMESTAMP,
    title       VARCHAR (32)  NOT NULL,
    url         VARCHAR (64)  NOT NULL,
    tags        VARCHAR (64)  NOT NULL,
    ingredients TEXT          NOT NULL,
    recipe      TEXT          NOT NULL,
    image       VARCHAR (255) NOT NULL
);"""


@app.route('/create_tag', methods=['POST'])
def create_tag():
    tag_name = request.form['new_tag'].lower()
    do_new_tag(tag_name)
    return redirect(url_for('index'))


@app.route('/search', methods=['POST'])
def search():
    title = request.form['search_content']
    recipe_content = get_post_title(title.title())
    return redirect('/' + recipe_content['url'])


@app.route('/searchone', methods=['GET'])
def searchone():
    title = request.args.get('tags')
    recipes = get_recipe_tag(title)
    all_tags = get_all_tags()
    return render_template("index.html", recipes=recipes, all_tags=all_tags)


if __name__ == '__main__':
    app.run(debug=True, port=5002)
