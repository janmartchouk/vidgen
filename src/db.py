import sqlite3
import pickle
import logging
import os

from config import structure
from utils.logger import setup_logger
from models.post import Post

class DB:
    def __init__(self, loglevel = logging.INFO):
        self.logger = setup_logger(__name__, loglevel, emoji='📚')

        # if db path invalid, exit
        if not structure.DB_PATH:
            self.logger.error("No DB_PATH configured in config")
            exit(1)
        elif not os.path.isfile(structure.DB_PATH):
            self.logger.info("DB_PATH does not exist, creating")
            open(structure.DB_PATH, 'w').close()

        self.conn = sqlite3.connect(structure.DB_PATH)
        self.c = self.conn.cursor()

        self.c.execute("CREATE TABLE IF NOT EXISTS posts (hash text, data blob)")

        self.logger.info("Connected to DB")
    
    def __del__(self): 
        self.close()

    def close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.logger.info("DB connection closed")

    # Fetch Post by hash from db
    def get_post_by_hash(self, hash):
        """
        Fetch a Post object from the database by its hash.

        :param hash: The hash of the post to fetch.
        :return: The Post object if found, None otherwise.
        """

        self.logger.debug(f"Fetching post with hash {hash}")

        self.c.execute("SELECT * FROM posts WHERE hash=?", (hash,))
        result = self.c.fetchone()

        if result:
            hash, data = result
            self.logger.debug(f"Found post with hash {hash}")
            return pickle.loads(data)
        else:
            self.logger.debug(f"Could not find post with hash {hash}")
            return None

    # Insert a Post object into DB
    def insert_post(self, post: Post):
        """
        Insert a Post object into the database.

        :param post: The Post object to insert.
        """

        self.logger.debug(f"Inserting post with hash {post.hash}")

        self.c.execute("INSERT INTO posts VALUES (?, ?)", (post.hash, pickle.dumps(post)))
        self.conn.commit()

        self.logger.debug(f"Successfully inserted post with hash {post.hash}")

    # Update a Post object in DB
    def update_post(self, post: Post):
        """
        Update a Post object in the database.

        :param post: The Post object to update.
        """

        self.logger.debug(f"Updating post with hash {post.hash}")

        self.c.execute("UPDATE posts SET data=? WHERE hash=?", (pickle.dumps(post), post.hash))
        self.conn.commit()

        self.logger.debug(f"Successfully updated post with hash {post.hash}")

    # Delete a Post object from DB
    def delete_post(self, post: Post):
        """
        Delete a Post object from the database.

        :param post: The Post object to delete.
        """

        self.logger.debug(f"Deleting post with hash {post.hash}")

        self.c.execute("DELETE FROM posts WHERE hash=?", (post.hash,))
        self.conn.commit()

        self.logger.debug(f"Successfully deleted post with hash {post.hash}")

    # Update a Post in DB
    def update_post(self, post: Post):
        """
        Update a Post object in the database.

        :param post: The Post object to update.
        :param loglevel: The log level for logging messages (default: logging.INFO).
        """

        self.logger.debug(f"Updating post with hash {post.hash}")

        self.c.execute("UPDATE posts SET data=? WHERE hash=?", (pickle.dumps(post), post.hash))
        self.conn.commit()

        self.logger.debug(f"Successfully updated post with hash {post.hash}")

    def get_all_posts(self):
        """
        Get all Post objects from the database.

        :return: A list of Post objects.
        """

        self.logger.debug("Fetching all posts")

        self.c.execute("SELECT * FROM posts")
        result = self.c.fetchall()

        posts = []

        for hash, data in result:
            posts.append(pickle.loads(data))

        self.logger.debug(f"Found {len(posts)} posts")

        return posts