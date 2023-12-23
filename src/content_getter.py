import feedparser
import logging
import time
import requests

from bs4 import BeautifulSoup
from tqdm import tqdm

from config.dicts import SUBREDDITS
from utils.logger import setup_logger
from models.post import Post

class ContentGetter:
    def __init__(self, loglevel = logging.INFO):
        self.logger = setup_logger(__name__, loglevel, emoji='🌍')

    # Get a list of Reddit Posts from an RSS feed
    def from_subreddit(self, subreddit):
        if not subreddit in SUBREDDITS:
            self.logger.error(f"{subreddit} is not configured")
            exit(1)

        if SUBREDDITS[subreddit] == 'rss':
            return self.from_rss_subreddit(subreddit)
        elif SUBREDDITS[subreddit] == 'web':
            return self.from_web(subreddit)
        else:
            self.logger.error(f"{subreddit} is not configured properly")
            exit(1)

    def from_rss_subreddit(self, subreddit):
        data = feedparser.parse(f'https://reddit.com/r/{subreddit}/top.rss')
        posts = []
        failed_number = 0
        if data.entries:
            try:
                for entry in data.entries:
                    paragraphs = BeautifulSoup(entry.content[0].value, 'html.parser').find_all('p')
                    content = ''.join([p.get_text() for p in paragraphs])
                    post_obj = Post(
                        title=entry.title,
                        author=entry.authors[0].name,
                        subreddit=subreddit,
                        content=content,
                        crawl_date=time.time()
                    )
                    posts.append(post_obj)
                    self.logger.debug(f"RSS crawled the post {post_obj.short_hash}")
            except Exception as e:
                failed_number += 1
                self.logger.debug(f"Continuing, but encountered an error parsing RSS feed: {e}")
        self.logger.info(f"RSS crawled {len(posts)} posts from {subreddit} ({failed_number} failed)")
        return posts
    
    def from_web(self, subreddit):
        soup = BeautifulSoup(requests.get(f'https://reddit.com/r/{subreddit}/top').content, 'html.parser')
        posts = []
        failed_number = 0
        for post in soup.find_all('shreddit-post'):
            try:
                post_obj = Post(
                    title=post.find('a', id=lambda x: x and 'post-title' in x).text,
                    author=post.find('span', {'slot': 'authorName'}).text,
                    subreddit=subreddit,
                    content=post.find('div', id=lambda x: x and 'post-rtjson-content' in x).text,
                    crawl_date=time.time()
                )
                posts.append(post_obj)
                self.logger.debug(f"Web crawled the post {post_obj.short_hash}")
            except Exception as e:
                failed_number += 1
                self.logger.debug(f"Continuing, but encountered an error parsing web feed: {e}")
        self.logger.info(f"Web crawled {len(posts)} posts from {subreddit} ({failed_number} failed)")
        return posts