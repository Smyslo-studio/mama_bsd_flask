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
    recipes = databaseGet.get_all_posts()
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
    all_tags = databaseGet.get_all_tags()
    return render_template("index.html", recipes=recipes, all_tags=all_tags)


@app.route('/<recipe_url>')
def recipe(recipe_url):
    recipe_content = databaseGet.get_one_post_with_url(str(recipe_url))
    tags = recipe_content['tags']
    tags = tags.split(',')
    print(tags)
    ingredients = recipe_content['ingredients']
    ingredients_dist = json.loads(ingredients)
    return render_template('recipe.html', tags=tags, recipe=recipe_content, ingredients=ingredients_dist)


@app.route('/<recipe_url>/edit', methods=('POST', 'GET'))
def edit(recipe_url):
    tags = databaseGet.get_all_tags()
    post = databaseGet.get_one_post_with_url(recipe_url)
    using_tags_list, unusing_tags_list = using_tags(recipe_url)
    return render_template('create.html', recipe=post, tags=tags, page_title="Редактирование", use_tags=using_tags_list, unusing_tags=unusing_tags_list)


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
        databasePost.post_new_recipe(title, recipe_url, tags2, ingredient_list, recipe_content, image_path)

        recipe_content = databaseGet.get_one_post_with_url(recipe_url)
        recipe_id = recipe_content['id']
        databasePost.connect_tags_id_and_recipe_id_and_add_to_tag_recipe(recipe_id, tags)
    return redirect(url_for('index'))


@app.route('/create_tag', methods=['POST'])
def create_tag():
    tag_name = request.form['new_tag'].lower()
    databasePost.post_new_tag(tag_name)
    return redirect(url_for('index'))


@app.route('/search', methods=['POST'])
def search():
    title = request.form['search_content']
    recipes = databaseGet.search_posts_with_title(title.title())
    all_tags = databaseGet.get_all_tags()
    return render_template("index.html", recipes=recipes, all_tags=all_tags)


@app.route('/searchone', methods=['GET'])
def searchone():
    tag_id = request.args.get('tags')
    recipes = databaseGet.get_recipe_with_tag_id(tag_id)
    all_tags = databaseGet.get_all_tags()
    return render_template("index.html", recipes=recipes, all_tags=all_tags)


if __name__ == '__main__':
    app.run(debug=True, port=5002)
