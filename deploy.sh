ENDPOINT=''

case $TRAVIS_BRANCH in
  "master") ENDPOINT='https://pawprints.rit.edu/deploy';;
  "develop") ENDPOINT='https://sgstage.rit.edu/deploy';;
esac

curl -u "$USERNAME":"$PASSWORD" -d '{"author": "'"$AUTHOR_NAME"'", "email": "'"$COMMITTER_EMAIL"'"}' $ENDPOINT;
