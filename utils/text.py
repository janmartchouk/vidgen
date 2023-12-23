import re #split_text_into_chunks

def replace_words(text, replacement_dict):
    """
    Replaces words in the given text based on the provided replacement dictionary.

    Args:
        text (str): The input text to be processed.
        replacement_dict (dict): A dictionary containing word replacements, where the keys are the words to be replaced
                                and the values are the replacement words.

    Returns:
        str: The text with the specified words replaced.

    """
    for k, v in replacement_dict.items():
        text = text.lower().replace(k.lower(), v)
    return text

def split_text_into_chunks(text, max_chunk_length=300):
    """
    Split a given text into chunks of a maximum character count.

    Args:
        text (str): The text to be split into chunks.
        max_chunk_length (int, optional): The maximum character count for each chunk. Defaults to 300.

    Returns:
        list: A list of chunks, where each chunk is a string.

    Example:
        >>> text = "This is a sentence. This is another sentence. This is a third sentence."
        >>> split_text_into_chunks(text, max_chunk_length=20)
        ['This is a sentence.', ' This is another', ' sentence. This is a', ' third sentence.']
    """
    
    # Use regex to find sentence boundaries
    sentence_pattern = re.compile(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s")

    # Find sentence boundaries in the text
    sentence_boundaries = sentence_pattern.split(text)

    # Initialize chunks and current_chunk
    chunks = []
    current_chunk = ""

    for sentence in sentence_boundaries:
        sentence = sentence.replace('.', '. ') # make sure there are no weird.dots inside the sentences
        # Check if adding the current sentence to the current_chunk exceeds the max_chunk_length
        if len(current_chunk) + len(sentence) <= max_chunk_length:
            current_chunk += ' ' + sentence # same as the replace above
        else:
            # If it exceeds, start a new chunk with the current sentence
            chunks.append(current_chunk)
            current_chunk = sentence

    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def shorten_string(input_string, max_length=20):
    """
    Shortens a given input string to a maximum length, appending '...' if necessary.

    Args:
        input_string (str): The input string to be shortened.
        max_length (int, optional): The maximum length of the shortened string. Defaults to 20.

    Returns:
        str: The shortened string.

    Example:
        >>> shorten_string("This is a sentence.", max_length=10)
        'This is a...'
    """
    if len(input_string) <= max_length:
        return input_string
    else:
        return input_string[:max_length-3] + '...'

def shorten_hash(sha_string, prefix_length=6, suffix_length=6):
    """
    Shortens a SHA string by truncating it and adding ellipsis in the middle.
    
    Args:
        sha_string (str): The SHA string to be shortened.
        prefix_length (int): The length of the prefix to keep. Default is 6.
        suffix_length (int): The length of the suffix to keep. Default is 6.
    
    Returns:
        str: The shortened SHA string.

    Example:
        >>> shorten_hash("1234567890abcdef", prefix_length=4, suffix_length=4)
        '1234...cdef'
    """
    if len(sha_string) <= prefix_length + suffix_length:
        return sha_string
    else:
        return f"{sha_string[:prefix_length]}...{sha_string[-suffix_length:]}"
