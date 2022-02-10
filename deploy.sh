if [ $TRAVIS_BRANCH = "master" ]; then
  curl -u $USERNAME:$PASSWORD -d '{"author": "'"$AUTHOR_NAME"'", "email": "'"$COMMITTER_EMAIL"'"}' https://pawprints.rit.edu/deploy -k;
  exit 0;
elif [ $TRAVIS_BRANCH = "develop" ]; then
  curl -u $USERNAME:$PASSWORD -d '{"author": "'"$AUTHOR_NAME"'", "email": "'"$COMMITTER_EMAIL"'"}' https://sgstage.rit.edu/deploy -k;
fi
