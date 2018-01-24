"""
Provides functionality to see if a petition contains profanities.
Author: Peter Zujko

"""
import csv
import os
import re


def load_words(filename):
    """
    Loads words from csv to list
    """
    words = []
    dirname = os.path.dirname(__file__)
    csvfile = open(os.path.join(dirname, filename), 'r')
    for line in csvfile:
        words.append(line.strip())
    csvfile.close()
    return words


def has_profanity(petition_body):
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
