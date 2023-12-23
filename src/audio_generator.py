import random
import os
import sys
import logging

from pydub import AudioSegment
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
import tempfile

from utils.tiktok_tts import tts as tiktok_tts
from utils.logger import setup_logger
from models.post import Post
from config.structure import AUDIO_DIR
from config.dicts import TIKTOK_VOICES
from utils.text import split_text_into_chunks, shorten_hash, shorten_string

class AudioGenerator:
    def __init__(self, loglevel = logging.INFO):
        self.logger = setup_logger(__name__, loglevel, emoji='🎵')
        self.output_dir = AUDIO_DIR

    def from_post(self, post):
        """
        Generate audio from a post.
        
        Args:
            post (Post): The post content to generate audio from.
        
        Returns:
            bool: True if audio generation is successful, False otherwise.
        """

        voice = random.choice(TIKTOK_VOICES)
        texts = [post.title] + split_text_into_chunks(post.content)

        segments = AudioSegment.empty()

        with tempfile.TemporaryDirectory() as tmpdirname:
            try:
                for i, t in enumerate(texts):
                    filename = os.path.join(tmpdirname, f"{i}out.mp3")

                    sys.stdout = open(os.devnull, 'w') # block tiktok_tts print() spam
                    tiktok_tts(t, voice, filename, play_sound=False)
                    sys.stdout = sys.__stdout__ # restore printing

                    segments += AudioSegment.from_file(filename, format='mp3')

                audio_path = os.path.join(self.output_dir, f'{post.hash}.mp3')
                segments.export(audio_path)
                self.logger.debug(f"Generated audio for post {post.short_hash}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to generate audio for post {post.short_hash}: {e}")
                return False
