"""
Provides functionality to see if a petition contains profanities.
Author: Peter Zujko
"""
import os
import re



def load_words(filename):
    """
    Loads words from csv to list
    """
    with open(os.path.join(os.path.dirname(__file__), filename), 'r') as csvfile:
        return [line.strip() for line in csvfile]


def has_profanity(text):
    profanities = load_words('profanity.csv')
    petition_body = re.sub(r"<[^<]+?>", "", text)

    # TODO: This is a bad way to do this. It's not efficient and it's not accurate.
    # profanity-check pip package is a better way to do this.
    for word in petition_body.split(' '):
        if re.sub(r"[^a-zA-Z]+", "", word).lower() in profanities:
            return True
    return False

