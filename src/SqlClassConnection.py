import sqlite3


class DatabaseGet(object):

    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def get_all_posts(self):
        posts = self.cursor.execute('SELECT * FROM recipes').fetchall()
        return posts

    def get_posts_from_to(self, qua_f, qua_t):
        posts = self.cursor.execute('SELECT * FROM recipes LIMIT ' + str(qua_f) + ', ' + str(qua_t)).fetchall()
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

    def search_posts_with_ingredient(self, ingredient):
        posts = self.cursor.execute("""SELECT * FROM recipes
                                        INNER JOIN ingredients ON recipes.id = ingredients.recipe_id
                                        WHERE ingredients.ingredient LIKE ?""", ("%" + ingredient + "%",)).fetchall()
        return posts

    def get_ingredients_to_recipe_by_recipe_id(self, recipe_id):
        ingredients = self.cursor.execute("SELECT * FROM ingredients WHERE recipe_id=?", (recipe_id,)).fetchall()
        return ingredients

    def get_q_all_recipes(self):
        q = self.cursor.execute("SELECT COUNT(1) from recipes").fetchone()[0]
        return q

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

    def post_new_recipe(self, title, url, tags, recipe_content, image_name, source):
        _SQL = """insert into recipes
            (title, url, tags, recipe, image, source)
            values
            (?, ?, ?, ?, ?, ?)"""
        self.cursor.execute(_SQL, (title, url, tags, recipe_content, image_name, source))
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
        post = self.cursor.execute('SELECT * FROM recipes WHERE url = ?', (url,)).fetchone()
        self.cursor.execute('DELETE FROM tags_recipes WHERE recipe = ?', (post['id'],))
        self.cursor.execute('DELETE FROM recipes WHERE url = ?', (url,))
        self.cursor.execute('DELETE FROM ingredients WHERE recipe_id = ?', (post['id'],))
        self.connection.commit()

    def delete_tag_with_tag_id(self, tag_id):
        self.cursor.execute('DELETE FROM tags WHERE id = ?', (tag_id,))
        self.cursor.execute('DELETE FROM tags_recipes WHERE tag = ?', (tag_id,))
        self.connection.commit()

    def add_ingredient_to_db_with_list(self, recipe_id, ingredient_list, quantity_list, quantity_spoon_list):
        _SQL = """INSERT INTO ingredients
                (recipe_id, ingredient, quantity, quantity_spoon)
                VALUES
                (?, ?, ?, ?)"""
        for i in range(len(ingredient_list)):
            self.cursor.execute(_SQL, (recipe_id, ingredient_list[i], quantity_list[i], quantity_spoon_list[i]))
            self.connection.commit()

    def __del__(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
