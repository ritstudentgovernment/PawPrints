"""
Provides functionality to see if a petition contains profanities.
Author: Peter Zujko

"""
import os
import re


def load_words(filename: str) -> list:
    """
    Loads words from csv to list
    """
    with open(os.path.join(os.path.dirname(__file__), filename), "r") as csv_file:
        return [
            line.strip() for line in csv_file
        ]


def has_profanity(petition_body: str) -> bool:
    profanities = load_words('profanity.csv')
    petition_body = re.sub(r"<[^<]+?>", "", petition_body)

    body = petition_body.split(' ')

    index = 0
    for word in body:
        word = re.sub(r"[^a-zA-Z]+", "", word)
        word = word.lower()
        if word in profanities:
            return True
        index += 1
    return False
