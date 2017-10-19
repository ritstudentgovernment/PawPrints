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

    print(type(body))
    print(type(petition_body))

    index = 0
    for word in body:
        print("Is word " + index + " (" + word + ") profane?")
        for profanity in profanities:
            if profanity == word:
                print("YES, that word should be cast to the depths of H3ll.")
                return True
        print("No. That word is totally biblical.")
    return False
