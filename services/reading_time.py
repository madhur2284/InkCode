import math

def reading_time(content: str):
    """Average reading time of adults are 200 words per minute"""
    word_count = len(content.split())
    minutes = math.ceil(word_count/200)
    return minutes
