import whisper
import logging

from utils.logger import setup_logger
from config.structure import AUDIO_DIR, SUBTITLE_DIR
from utils.text import shorten_hash

class Subtitler:
    def __init__(self, loglevel = logging.INFO):
        self.logger = setup_logger(__name__, loglevel, emoji='📝')
        self.model = whisper.load_model('small.en')
        self.writer = whisper.utils.WriteSRT(SUBTITLE_DIR)

    def from_post(self, post):
        if post.audio and not post.subtitles:
            return self.from_hash(post.hash)
        elif not post.audio:
            self.logger.debug(f"Skipping subtitle generation for post {shorten_hash(post.hash)} because it has no audio")
            return False
        elif post.subtitles:
            self.logger.debug(f"Skipping subtitle generation for post {shorten_hash(post.hash)} because it already has subtitles")
            return True
        
    def from_hash(self, hash):
        """
        Generate subtitles from a post hash.

        Args:
            hash (str): The hash of the post to generate subtitles from.
        
        Returns:
            bool: True if subtitle generation is successful, False otherwise.
        """
        try:
            result = self.model.transcribe(f'{AUDIO_DIR}/{hash}.mp3')
            self.writer(result, f'{SUBTITLE_DIR}/{hash}.srt')
            self.logger.debug(f"Generated subtitles for post {shorten_hash(hash)}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to generate subtitles for post {shorten_hash(hash)}: {e}")
            return False
