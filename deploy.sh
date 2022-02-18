#!/bin/bash

# This is a script that will deploy pawprints if ran inside the ./PawPrints directory AFTER the master branch has been merged with develop!

#pulling all of the new code that was merged into master in the github repo
git pull

# restarting the container to implement the code changes pulled from the github repo
docker container restart pawprints_web_1
