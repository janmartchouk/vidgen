import logging
import time
import argparse
import concurrent.futures
import json
import os

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from utils.youtube_uploader import YouTubeUploader
from src.content_getter import ContentGetter
from config.dicts import SUBREDDITS
from config.structure import VIDEO_DIR
from src.db import DB
from utils.logger import setup_logger
from src.audio_generator import AudioGenerator
from src.subtitler import Subtitler
from src.composer import Composer
from utils.text import shorten_string

def update_db(logger, db: DB):
    """
    Update the DB with new Posts from Reddit.
    """
    start = time.time()
    logger.info("Updating DB")
    cg = ContentGetter(loglevel=logging.INFO)

    new_insertions = 0

    with logging_redirect_tqdm(loggers = [logger, cg.logger, db.logger]):
        for subreddit in tqdm(SUBREDDITS, desc="Subreddits", leave=False):
            for post in tqdm(cg.from_subreddit(subreddit), desc="Posts", leave=False):
                if not db.get_post_by_hash(post.hash):
                    db.insert_post(post)
                    new_insertions += 1

                    if args.quick and new_insertions >= args.quick_limit:
                        logger.debug(f"Quick mode: Stopping after {new_insertions} new insertions")
                        break

            if args.quick and new_insertions >= args.quick_limit:
                break

    end = time.time()

    logger.info(f"DB Update complete. Inserted {new_insertions} new Posts. Finished in {end - start} seconds")

def generate_audio(logger, db: DB, num_threads=16):
    """
    Generate audio from Posts in the DB using multiple threads.
    """
    start = time.time()
    logger.info("Generating audio")
    ag = AudioGenerator(loglevel=logging.INFO)

    failed_number = 0
    successes = 0

    all_posts = db.get_all_posts()
    if args.quick:
        all_posts = all_posts[:args.quick_limit] # only work on quick_limit posts in quick mode
    num_posts=len(all_posts)
    bar = tqdm(total=num_posts, desc="Audios", leave=False)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor, logging_redirect_tqdm(loggers=[logger, ag.logger, db.logger]):
        future_to_post = {executor.submit(process_individual_post, post, ag, post.audio): post for post in all_posts}

        for future in concurrent.futures.as_completed(future_to_post):
            post = future_to_post[future]
            bar.set_postfix_str(post.short_hash) #update progressbar
            try:
                result = future.result()
                if result:
                    post.audio = True
                    db.update_post(post) #TODO
                    successes += 1

                    if args.quick and successes >= args.quick_limit:
                        logger.debug(f"Quick mode: Stopping after {successes} successes")
                        break
                else:
                    failed_number += 1
                    logger.debug(f"Failed to generate audio for post {post.short_hash} -- Deleting from DB")
                    db.delete_post(post) #TODO

            except Exception as exc:
                logger.error(f"Error processing post {post.short_hash}: {exc}")

            finally:
                bar.update(1) #update progressbar

    end = time.time()
    bar.close()
    logger.info(f"Generated audio for {successes} Posts ({failed_number} failed). Finished in {end - start} seconds ({(end - start) / successes} seconds per Post)")

def process_individual_post(post, generator, property):
    if not property:
        if generator.from_post(post):
            return True
        else:
            return False
    return True

def generate_subtitles(logger, db: DB):
    """
    Generate subtitles from Posts in the DB.
    """

    ### We cannot multithread this well since Subtitler uses a
    ### full machine learning model loaded into RAM in the background.
    ### For multiple threads, we would need to load it multiple times. bad idea.
    ### If you implement Subtitler() to, i.e., use a server such as the whisper API,
    ### then you can multithread this

    start = time.time()
    logger.info("Generating subtitles")
    st = Subtitler(loglevel=logging.INFO)

    failed_number = 0
    successes = 0

    with logging_redirect_tqdm(loggers = [logger, st.logger, db.logger]):
        for post in tqdm(db.get_all_posts(), desc="Posts", leave=False):
            if st.from_post(post):
                post.subtitles = True
                db.update_post(post)
                successes += 1

                if args.quick and successes >= args.quick_limit:
                    logger.debug(f"Quick mode: Stopping after {successes} successes")
                    break

            else:
                failed_number += 1
                logger.debug(f"Failed to generate subtitles for post {post.short_hash} -- Deleting from DB")
                db.delete_post(post)

    end = time.time()
    logger.info(f"Generated subtitles for {successes} Posts ({failed_number} failed). Finished in {end - start} seconds ({(end - start) / successes} seconds per Post)")

def compose_video(logger, db:DB, num_threads=16):
    """
    Compose video from Posts in the DB.
    """
    """
    Compose video from Posts in the DB using multiple threads.
    """
    start = time.time()
    logger.info("Composing video")
    vc = Composer(loglevel=logging.INFO) # video composer

    failed_number = 0
    successes = 0

    all_posts = db.get_all_posts()
    if args.quick:
        all_posts = all_posts[:args.quick_limit]  # only work on quick_limit posts in quick mode
    num_posts = len(all_posts)
    bar = tqdm(total=num_posts, desc="Videos", leave=False)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor, logging_redirect_tqdm(loggers=[logger, vc.logger, db.logger]):
        future_to_post = {executor.submit(process_individual_post, post, vc, post.video): post for post in all_posts}

        for future in concurrent.futures.as_completed(future_to_post):
            post = future_to_post[future]
            bar.set_postfix_str(post.short_hash)  # update progress bar
            try:
                result = future.result()
                if result:
                    post.video = True
                    # db.update_post(post)  # Uncomment and implement if needed
                    successes += 1

                    if args.quick and successes >= args.quick_limit:
                        logger.debug(f"Quick mode: Stopping after {successes} successes")
                        break
                else:
                    failed_number += 1
                    logger.debug(f"Failed to compose video for post {post.short_hash} -- Deleting from DB")
                    # db.delete_post(post)  # Uncomment and implement if needed

            except Exception as exc:
                logger.error(f"Error processing post {post.short_hash}: {exc}")

            finally:
                bar.update(1)  # update progress bar

    end = time.time()
    bar.close()
    logger.info(f"Composed video for {successes} Posts ({failed_number} failed). Finished in {end - start} seconds ({(end - start) / successes} seconds per Post)")

def upload_to_youtube(logger, db: DB):
    """
    Upload videos to YouTube.
    """
    pass

    # This is broken right now. :(

    # all_posts = db.get_all_posts()
    # if args.quick:
    #     all_posts = all_posts[:args.quick_limit]

    # for post in all_posts:
    #     if post.uploaded_youtube:
    #         logger.debug(f"Skipping YouTube upload for post {post.short_hash} because it is already uploaded")
    #         continue
    #     parts_folder = os.path.join(VIDEO_DIR, f"{post.hash}_parts")
    #     parts_filenames = os.listdir(parts_folder)
    #     for num, file in enumerate(parts_filenames):
    #         youtube_title = f"{post.title} (Part {num+1}/{len(parts_filenames)})"
    #         youtube_title = shorten_string(youtube_title, max_length=110)
    #         metadata = {
    #             'title': youtube_title,
    #             'description': f"Posted by {post.author} in /r/{post.subreddit} #shorts",
    #             'tags': ['shorts']
    #         }
    #         uploader = YouTubeUploader(os.path.join(parts_folder, file), metadata_dict=metadata, loglevel = logging.DEBUG)
    #         try:
    #             was_uploaded, id = uploader.upload()
    #             assert was_uploaded
    #             post.uploaded_youtube = True
    #             db.update_post(post)
    #             logger.debug(f'Uploaded to YouTube at id {id} -- {post.short_hash}')
    #         except Exception as exc:
    #             logger.error(f'Failed to upload {post.short_hash} to YouTube: {exc}')
        

if __name__ == '__main__':
    # get commandline arguments
    parser = argparse.ArgumentParser(description='Crawl Reddit and generate audio')
    parser.add_argument('--no-audio', dest='no_audio', action='store_true', help='Do not generate audio')
    parser.add_argument('--no-web-update', dest='no_web', action='store_true', help='Do not update DB with new Posts from Reddit')
    parser.add_argument('--quick', dest='quick', action='store_true', help=f'Only do limited Posts (--quick-limit, default 1) (for testing purposes')
    parser.add_argument('--no-subtitles', dest='no_subtitles', action='store_true', help='Do not generate subtitles')
    parser.add_argument('--no-video', dest='no_video', action='store_true', help='Do not compose video')
    parser.add_argument('--quick-limit', dest='quick_limit', type=int, default=1, help='Number of Posts to do (for testing purposes)')
    parser.add_argument('--no-youtube-upload', dest='no_youtube_upload', action='store_true', help='Do not upload to YouTube')
    args = parser.parse_args()

    global_start = time.time()
    logger = setup_logger(__name__, logging.INFO, emoji='👑')
    db = DB(loglevel=logging.INFO)

    if not args.no_web:
        update_db(logger, db)
    
    if not args.no_audio:
        generate_audio(logger, db)

    if not args.no_subtitles:
        generate_subtitles(logger, db)

    if not args.no_video:
        compose_video(logger, db)

    if not args.no_youtube_upload:
        upload_to_youtube(logger, db)