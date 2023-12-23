# Typical Reddit Slang which will be replaced with non-nerdy counterparts
REDDIT_SLANG = {
    'tifu': 'Today I f\'ed up',
    'ilpt': 'Illegal Life Pro Tip',
    'ulpt': 'Unethical Life Pro Tip',
    'lpt': 'Life Pro Tip',
    'aita': 'Am I The Asshole',
    'til': 'Today I Learned',
    'tl,dr': 'In Summary;',
    'tldr': 'In Summary;',
    'cuz': 'because',
    'f*cked': 'f\'ed',
    'f*ck': 'f',
}

# Voices to select from. More can be found at https://github.com/oscie57/tiktok-voice/wiki/Voice-Codes
TIKTOK_VOICES = [   
                    'en_uk_001',                  # English UK - Male 1
                    'en_uk_003',                  # English UK - Male 2
                    'en_us_001',                  # English US - Female (Int. 1)
                    'en_us_002',                  # English US - Female (Int. 2)
                    'en_us_006',                  # English US - Male 1
                    'en_us_007',                  # English US - Male 2
                    'en_us_009',                  # English US - Male 3
                    'en_us_010',                  # English US - Male 4
                ]

# Posts which include any of these words will be ignored
BAD_WORDS = [
    'suicide',
    'kill',
    'dick',
    'balls'
]

# These subreddits will be queried for the daily top posts
# Using either RSS or Web-Scraping (if the subreddit does not support RSS)
SUBREDDITS = {
    'tifu': 'rss',
    'confession': 'rss',
    'relationship_advice': 'web',
    'amitheasshole': 'rss'
}