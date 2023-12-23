import hashlib
import re

from config.dicts import REDDIT_SLANG
from utils.text import shorten_string, shorten_hash, replace_words

class Post:
    """
    A class representing a Reddit post.
    """
    def __init__(self, title, author, subreddit, content, crawl_date):
        """
        Initialize a Post object.

        :param title: The title of the post.
        :type title: str
        :param author: The author of the post.
        :type author: str
        :param subreddit: The subreddit of the post.
        :type subreddit: str
        :param content: The content of the post.
        :type content: str
        :param crawl_date: The date the post was crawled.
        :type crawl_date: datetime.datetime
        
        """
        # Simple data stores
        self.author = author
        self.subreddit = subreddit
        self.crawl_date = crawl_date

        # Replace Reddit slang in title and content
        self.title = replace_words(title, REDDIT_SLANG)
        self.content = replace_words(content, REDDIT_SLANG)

        # Remove Age/Gender Reddit-typical tuples
        self.title = re.sub(r"\(?\d{1,3}[mfMF]\)?", '', self.title).strip()
        self.content = re.sub(r"\(?\d{1,3}[mfMF]\)?", '', self.content).strip()

        # Clean up potentially spammy fields
        self.author = self.author.replace('\n', ' ').replace('\t', ' ')
        self.author = re.sub(' +', ' ', self.author).strip()
        self.title = self.title.replace('\n', ' ').replace('\t', ' ')
        self.title = re.sub(' +', ' ', self.title).strip()
        self.content = self.content.replace('\n', ' ').replace('\t', ' ')
        self.content = re.sub(' +', ' ', self.content).strip()

        # Calculate hash from title + author + post
        self.hash = hashlib.sha256(
            str.encode(self.title) + str.encode(self.author) +
            str.encode(self.subreddit)
        ).hexdigest()

        # Shorten title and hash
        self.short_title = shorten_string(self.title)
        self.short_hash = shorten_hash(self.hash)

        # By default, we don't have a generated audio, subtitles or video yet
        self.audio = False
        self.subtitles = False
        self.video = False
        self.uploaded_youtube = False

        # Used for storing which platforms the post has been uploaded to
        self.posted_to = []

    def __str__(self, short=True) -> str:
        return f"""{self.hash}
├── title:      {self.title},
├── author:     {self.author},
├── subreddit:  {self.subreddit},
├── content:    {shorten_string(self.content, max_length=50) if short else self.content},
└── crawl_date: {self.crawl_date})"""