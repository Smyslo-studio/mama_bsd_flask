from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort  # отображение ошибки
from werkzeug.utils import secure_filename  # проверка файла
from src import create_urls
from src.SqlClassConnection import DatabaseGet, DatabasePost
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


DB_LOCATION = "db/database.db"
databaseGet = DatabaseGet(DB_LOCATION)
databasePost = DatabasePost(DB_LOCATION)


def using_tags(recipe_url):
    use_tags = databaseGet.get_tags_to_recipe(recipe_url)
    all_tags = databaseGet.get_all_tags()
    unusing_tags = []
    for tag in all_tags:
        if not tag['title'] in use_tags:
            unusing_tags.append(tag['title'])
    return use_tags, unusing_tags


@app.route('/', methods=('POST', 'GET'))
def index():
    recipes = databaseGet.get_posts_from_to(0, 100)
    i = 0
    recipes_list = [[], [], []]
    for res in recipes:
        if i > 2:
            i = 0
        recipes_list[i].append(res)
        i += 1

    all_tags = databaseGet.get_all_tags()
    return render_template("index.html", recipes=recipes_list, tags=all_tags, pagination_list=0)


@app.route('/<recipe_url>')
def recipe(recipe_url):
    recipe_content = databaseGet.get_one_post_with_url(str(recipe_url))
    tags = databaseGet.get_all_tags()
    ttr = databaseGet.get_tags_to_recipe(recipe_url)
    ingredients = databaseGet.get_ingredients_to_recipe_by_recipe_id(recipe_content['id'])
    return render_template('recipe.html', tags=tags, tags_to_recipe=ttr, recipe=recipe_content, ingredients=ingredients)


@app.route('/<recipe_url>/edit', methods=('POST', 'GET'))
def edit(recipe_url):
    tags = databaseGet.get_all_tags()
    post = databaseGet.get_one_post_with_url(recipe_url)
    using_tags_list, unusing_tags_list = using_tags(recipe_url)
    ingredients = databaseGet.get_ingredients_to_recipe_by_recipe_id(post['id'])
    return render_template('create.html', recipe=post, tags=tags, page_title="Редактирование", use_tags=using_tags_list, unusing_tags=unusing_tags_list, ingredients=ingredients)


@app.route('/<recipe_url>/delete', methods=['POST'])
def delete(recipe_url):
    recipe_content = databaseGet.get_one_post_with_url(recipe_url)
    databasePost.delete_post_with_url(recipe_url)
    flash('Рещепт "{}" был успешно удален!'.format(recipe_content['title']))
    return redirect(url_for('index'))


@app.route('/create', methods=['POST', 'GET'])
def create():
    tags = databaseGet.get_all_tags()
    return render_template('create.html', tags=tags, page_title="Создание")


@app.route('/save', methods=['POST'])
def save():
    ingredient_list = ''
    i = 0
    if request.method == 'POST':
        title = request.form['title']
        recipe_url = create_urls.do_url(title)
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = '../static/images/' + file.filename
        else:
            image_path = "../static/images/xleb.jpg"

        """
        while True:
            try:
                ingredient = request.form['ingredient' + str(i)]
                quantity = request.form['quantity' + str(i)]
                if not ingredient == '' and not quantity == '':
                    ingredient_list += ('"' + ingredient + '": ' + '"' + quantity + '", ')
                i += 1
            except KeyError:
                break
        ingredient_list = '{' + ingredient_list[:-2] + '}'"""

        ingredient_list = []
        quantity_list = []
        quantity_spoon_list = []

        while True:
            try:
                ingredient = request.form['ingredient' + str(i)]
                quantity = request.form['quantity' + str(i)]
                quantity_spoon = request.form['quantity_spoon' + str(i)]

                ingredient_list.append(ingredient)
                quantity_list.append(quantity)
                quantity_spoon_list.append(quantity_spoon)

                i += 1
            except KeyError:
                break

        tags2 = ''
        tags = request.form.getlist('tag')
        for i in tags:
            tags2 += i
            tags2 += '|'
        tags2 = tags2[:-1]
        recipe_content = request.form['recipe']
        source = request.form['source']

        databasePost.post_new_recipe(title, recipe_url, tags2, recipe_content, image_path, source)

        recipe_content = databaseGet.get_one_post_with_url(recipe_url)
        recipe_id = recipe_content['id']

        databasePost.add_ingredient_to_db_with_list(recipe_id, ingredient_list, quantity_list, quantity_spoon_list)

        databasePost.connect_tags_id_and_recipe_id_and_add_to_tag_recipe(recipe_id, tags)
    return redirect(url_for('index'))


@app.route('/create_tag', methods=['POST'])
def create_tag():
    tag_name = request.form['new_tag'].lower()
    databasePost.post_new_tag(tag_name)
    return redirect(url_for('index'))


@app.route('/search', methods=['GET'])
def search():
    title = request.args.get('title')
    tag_id = request.args.get('tag')
    ingredient = request.args.get('ingredient')
    page = request.args.get('page')
    if page:
        recipes = DatabaseGet  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    elif title:
        recipes = databaseGet.search_posts_with_title(title.title())
    elif tag_id:
        recipes = databaseGet.get_recipe_with_tag_id(tag_id)
    elif ingredient:
        recipes = databaseGet.search_posts_with_ingredient(ingredient)
    else:
        recipes = 0
    all_tags = databaseGet.get_all_tags()
    return render_template("index.html", recipes=recipes, tags=all_tags)


if __name__ == '__main__':
    app.run(debug=True, port=5002)
