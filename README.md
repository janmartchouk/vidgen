# vidgen (video generator) ❤️‍🩹

This is a tool to algorithmically generate those videos you see all over TikTok, where some AI voice is reading out popular reddit posts while the background is some dopamine-rush mobile game footage.

### Example video generated by vidgen

https://github.com/janmartchouk/vidgen/assets/19735475/96b58fc4-c573-4f48-aac5-91b7506ae410

(this is cut off, the original output was about 5 minutes.)


### How does this work?

1. We get viral reddit posts from the Internet.

2. We put them through some text-to-speech program to make the computer say it so we have to think less.

3. We put that audio through a transcriber so we can put nice subtitles on the screen, our brain likes stimulation.
   
   (we need to re-transcribe the audio even though we have the source text because we don't know how fast the TTS is saying it, but we need to know when to put the subtitles on the screen)

4. We get some free-to-use satisfying game footage off YouTube and put everything together.

5. ???

6. Profit!

### Installation and tips

I recommend the use of a python virtual environment.
Create using `python3 -m venv .venv` while in the project root directory to create it in `.venv`, then, before use, do `source .venv/bin/activate`.
Install dependencies using `pip install -r requirements.txt`

This program requires `ffmpeg`, which you might need to install manually.

It expects `ffmpeg` to be compiled with CUDA support (for NVIDIA GPUs); if you do not have that, you might need to remove the relevant lines in `src/composer.py` (the ones with `hwaccel`).

`ffmpeg` is pretty intense on your CPU as well, if you do not have a fairly advanced one, the video composing step might take some time. On a Ryzen 5 CPU, one video of about 5 minutes length takes about 1 minute to compose.
Sometimes, `ffmpeg` shows scary red errors in the CLI, in my experience though, the videos turn out fine in the end. I don't know what is happening there.

The Subtitler uses OpenAI whisper on your local machine, which might load a fairly large model into your RAM. It works fine on my 16GB machine. If you have more or less than that, you might up- or downgrade to another model for faster/better processing or less load on your computer (you can change the model in `src/subtitler.py`).

### Usage

#### Directory structure

The program kind of expects the following directory structure under `data/`.

This means you're gonna want to provide a font.ttf and gonna need to provide background footage (for your convenience, by default, a libre font is provided.)

`audio/` is used for the text-to-speech output files

`db/` is populated with an sqlite3 database to store reddit posts

`subtitles/` is used for .srt files to store the generated subtitles

`ttf/` contains the font to be used

`video` contains
+ `bg/` which contains individual folders whichthen contain your background footage
+ `done/` which is populated with the generated videos

`config` contains
+ `dicts.py`, which are some dictionaries used to sanitize the reddit posts and, importantly, the list of subreddits used (currently: `r/tifu`, `r/amitheasshole`, `r/relationship_advice` and `r/confession`) and the method to query them (currently: `rss` or `web` -- as in RSS or web-scraping)
+ `structure.py`, which defines some directories and the font path, name and size.


`tree` output:

```
vidgen
│
├── config
│   ├── dicts.py
│   └── structure.py
│
├── audio
│   └── (filled by vidgen)
├── db
│   └── (filled by vidgen)
├── subtitles
│   └── (filled by vidgen)
├── ttf
│   └── subtitle_font.ttf
└── video
    ├── bg
    │   ├── gta_gameplay
    │   │   └── gta_footage.mp4
    │   └── some_other_background_footage
    │       └── some_other_footage.mp4
    └── done
        └── (filled by vidgen)
```

#### main.py

`main.py` provides a convenient way to use the program. By default:
1. it downloads the daily top posts from the subreddits provided in `config/dicts.py`, 
2. saves them into the DB, then, 
3. for each one, it generates a text-to-speech audio file, 
4. a subtitles `.srt` file, 
5. composes the audio with a random background video from `video/bg/random_folder/random_file`,
6. burns subtitles onto the composed file
7. cuts up that video into 50-second chunks (so they can be uploaded as YouTube shorts, for example.) 
8. (Planned) automatically uploads the parts to configured platforms

It takes the following options from the command line:

+ `--no-web`: Do not save new posts from the web
+ `--no-audio`: Do not generate audios
+ `--no-subtitles`: Do not generate subtitles
+ `--no-video`: Do not compose videos
+ `--no-youtube-upload`: Do not upload to YouTube (currently irrelevant)
+ `--quick`: Work on a limited number of posts only
+ `--quick-limit`: Set the limit used in `--quick`, default: 1

### Planned features

+ Automatically uploading generated videos to platforms such as YouTube (shorts), TikTok or Instagram (reels)
+ A web interface to manage the generation (and uploading)
+ More modular usage such as calling the program with a direct reddit link
+ More platforms for content apart from reddit (4chan greentexts? idk)

### Credits
(Giooorgiooo)[https://github.com/Giooorgiooo/TikTok-Voice-TTS] for the TikTok voice TTS
(weilbyte)[https://github.com/weilbyte] for providing the API endpoints for the TikTok voice
(OpenAI)[https://github.com/openai/whisper] for providing whisper free-of-charge, which is used for making the subtitles
(FFmpeg)[https://ffmpeg.org/] for providing the best general-purpose audio-video tool out there
