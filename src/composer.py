import logging
import subprocess
import random
import os

from utils.logger import setup_logger
from config.structure import AUDIO_DIR, SUBTITLE_DIR, VIDEO_DIR, BACKGROUNDS_DIR, FONT
from utils.text import shorten_hash

def get_duration(file):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file]
    return float(subprocess.check_output(cmd))

class Composer:
    def __init__(self, loglevel = logging.INFO):
        self.logger = setup_logger(__name__, loglevel, emoji='🎥')

    def from_post(self, post):
        if post.video:
            self.logger.debug(f"Skipping video generation for post {post.short_hash} because it already has a video")
            return True
        elif post.audio and post.subtitles:
            return self.from_hash(post.hash)
        else:
            self.logger.debug(f"Skipping video generation for post {post.short_hash} because it has no audio or subtitles")
            return False

    def from_hash(self, hash):
        """
        Generate a video from a post hash.

        Args:
            hash (str): The hash of the post to generate a video from.
        
        Returns:
            bool: True if video generation is successful, False otherwise.
        """
        try:
            ffmpeg_loglevel = 'info' if self.logger.getEffectiveLevel() == logging.DEBUG else 'error'

            audio_path = f'{AUDIO_DIR}/{hash}.mp3'
            subtitle_path = f'{SUBTITLE_DIR}/{hash}.srt'
            background_content_dir = os.path.join(BACKGROUNDS_DIR, random.choice([dir for dir in os.listdir(BACKGROUNDS_DIR) if os.path.isdir(os.path.join(BACKGROUNDS_DIR, dir))]))
            video_path = os.path.join(background_content_dir, random.choice([f for f in os.listdir(background_content_dir) if f.endswith('.mp4')]))

            audio_duration = get_duration(audio_path)
            video_duration = get_duration(video_path)

            # Calculate the maximum start time to ensure the remaining duration is sufficient for the voice-over
            max_start_time = int(video_duration - audio_duration)

            # Use ffmpeg to overlay the audio onto the video starting from a random time within the limits
            start_time = random.randint(0, max_start_time)
            composed_output_file =  os.path.join(VIDEO_DIR, f'{hash}_composed.mp4')
            # Use Multithreading to speed up the process
            cmd = ['ffmpeg', 
                 '-loglevel', ffmpeg_loglevel,
                 '-threads', 'auto',
                 '-hwaccel', 'cuda', #CUDA processing on NVIDA GPU
                 '-i', video_path, 
                 '-i', audio_path, 
                 '-filter_complex', f"[0:v]trim=start={start_time}:duration={audio_duration},setpts=PTS-STARTPTS[v0];[1:a]atrim=start=0:duration={audio_duration},asetpts=PTS-STARTPTS[a0]", 
                 '-map', "[v0]", 
                 '-map', "[a0]", 
                 '-c:v', 'h264_nvenc', 
                 '-c:a', 'aac', 
                 '-strict', 'experimental', 
                 composed_output_file
                ]
            subprocess.run(cmd)

            self.logger.debug(f"Composed AV - {shorten_hash(hash)}")

            # Burn subtitles onto the composed video
            composed_subtitled_output_file = os.path.join(VIDEO_DIR, f"{hash}_composed_subtitled.mp4")
            cmd = ['ffmpeg', 
                '-loglevel', ffmpeg_loglevel,
                '-threads', 'auto',
                '-hwaccel', 'cuda',
                '-i', composed_output_file, 
                '-vf', f"subtitles={subtitle_path}:force_style='Fontfile={FONT['PATH']},Fontname={FONT['NAME']},Fontsize={str(FONT['SIZE'])},MarginV=100,Alignment=6,PrimaryColor=&H00FFFFFF,OutlineColor=&H00FFFFFF'", 
                '-c:v', 'h264_nvenc',
                '-c:a', 'copy', 
                composed_subtitled_output_file
                ]
            subprocess.run(cmd)

            self.logger.debug(f"Burned subtitles - {shorten_hash(hash)}")

            os.remove(composed_output_file)

            # Split into 60 (50 for safety) Second parts for shorts
            parts_dir = os.path.join(VIDEO_DIR, f"{hash}_parts")
            if not os.path.exists(parts_dir):
                os.mkdir(parts_dir)
            composed_subtitled_output_part_file = os.path.join(parts_dir, f'%03d.mp4')
            cmd = ['ffmpeg', 
                   '-loglevel', ffmpeg_loglevel,
                   '-hwaccel', 'cuda',
                   '-threads', 'auto',
                   '-i', composed_subtitled_output_file, 
                   '-c', 'copy', 
                   '-f', 'segment', 
                   '-segment_time', '50', 
                   '-reset_timestamps', '1', 
                   composed_subtitled_output_part_file]
            subprocess.run(cmd)

        except Exception as e:
            self.logger.error(f"Failed to generate video for post {shorten_hash(hash)}: {e}")
            return False

        self.logger.debug(f"Cut into parts - {shorten_hash(hash)}")
        return True
