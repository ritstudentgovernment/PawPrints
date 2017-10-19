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
    csvfile = open(os.path.join(dirname,filename), 'r')
    for line in csvfile:
        words = line.strip().split(',')
    return words
        

def has_profanity(petition_body):
    profanities = load_words('profanity.csv')
    body = petition_body.split(' ')

    index = 0
    for word in body:
        re.sub("<[^<]+?>","",word)
        print("Is word " + str(index) + " (" + word + ") profane?")
        for profanity in profanities:
            if profanity == word.lower():
                print("YES, that word should be cast to the depths of H3ll.")
                return True
        print("No. That word is totally biblical.")
    return False
