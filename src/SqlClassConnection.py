import sqlite3


class DatabaseGet(object):

    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def get_all_posts(self):
        posts = self.cursor.execute('SELECT * FROM recipes').fetchall()
        return posts

    def get_one_post_with_url(self, url):
        post = self.cursor.execute('SELECT * FROM recipes WHERE url = ?', (url,)).fetchone()
        return post

    def get_one_post_with_title(self, title):
        post = self.cursor.execute('SELECT * FROM recipes WHERE title = ?', (title,)).fetchone()
        return post

    def get_all_tags(self):
        tags = self.cursor.execute("SELECT * FROM tags").fetchall()
        return tags

    def get_tags_to_recipe(self, url):
        tags_list = []
        tags = self.cursor.execute("""SELECT * FROM tags_recipes
                                    INNER JOIN recipes ON recipes.id = tags_recipes.recipe
                                    WHERE recipes.url=?""", (url,)).fetchall()
        for i in tags:
            tag = self.cursor.execute("""SELECT * FROM tags
                                                INNER JOIN tags_recipes ON tags_recipes.tag = tags.id
                                                WHERE tags.id=?""", (i['tag'],)).fetchone()
            tags_list.append(tag['title'])
        return tags_list

    def get_recipe_with_tag_id(self, recipe_id):
        content = self.cursor.execute("""SELECT * FROM recipes
                                        INNER JOIN tags_recipes ON recipes.id = tags_recipes.recipe
                                        INNER JOIN tags ON tags_recipes.tag = tags.id
                                        WHERE tags.id=?""", (recipe_id,)).fetchall()
        return content

    def search_posts_with_title(self, title):
        posts = self.cursor.execute("SELECT * FROM recipes WHERE title LIKE ?", ("%" + title + "%",)).fetchall()
        return posts

    def get_ingredients_to_recipe_by_recipe_id(self, recipe_id):
        ingredients = self.cursor.execute("SELECT * FROM ingredients WHERE recipe_id=?", (recipe_id,)).fetchall()
        return ingredients

    def __del__(self):
        print('Ok')
        self.cursor.close()
        self.connection.close()


class DatabasePost(object):

    def __init__(self, database_file):
        print(self)
        self.connection = sqlite3.connect(database_file, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def connect_tags_id_and_recipe_id_and_add_to_tag_recipe(self, recipe_id, tags):
        _SQL = """insert into tags_recipes
                (recipe, tag)
                values
                (?, ?)"""
        for tag in tags:
            tag_id = self.cursor.execute('SELECT id FROM tags WHERE title = ?', (tag,)).fetchone()
            tag_id = tag_id['id']  # без этого не работает, проверял
            self.cursor.execute(_SQL, (recipe_id, tag_id))
            self.connection.commit()

    def post_new_recipe(self, title, url, tags, ingredients, recipe_content, image_name, source):
        _SQL = """insert into recipes
            (title, url, tags, ingredients, recipe, image, source)
            values
            (?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.execute(_SQL, (title, url, tags, ingredients, recipe_content, image_name, source))
        self.connection.commit()

    def post_new_tag(self, tag_name):
        _SQL = """insert into tags
                    (title)
                    values
                    (?)"""
        self.cursor.execute(_SQL, (tag_name,))
        self.connection.commit()

    def edit_one_post(self, title, recipe, recipe_url):
        self.cursor.execute('UPDATE recipes SET title = ?, recipe = ? WHERE url = ?', (title, recipe, recipe_url))
        self.connection.commit()

    def delete_post_with_url(self, url):
        self.cursor.execute('DELETE FROM recipes WHERE url = ?', (url,))
        self.connection.commit()

    def __del__(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
