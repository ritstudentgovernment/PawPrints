"""
Provides functionality to see if a petition contains profanities. 
Author: Peter Zujko

"""
import csv
import os

def load_words(filename):
    """
    Loads words from csv to list
    """
    words = []
    dirname = os.path.dirname(__file__)
    csvfile = open(os.path.join(dirname,filename), 'r')
    for line in csvfile:
        words = line.strip().split(',')
    return words
        

def has_profanity(petition_body):
    profanities = load_words('profanity.csv')
    body = petition_body.split(' ')

    for word in body:
        for profanity in profanities:
            if profanity == word:
                return True
    return False
