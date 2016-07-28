#! /usr/bin/env bash

pip3.5 install -r requirements.txt

OUTFILE=".git/hooks/pre-commit"

echo "Creating .git/hooks folder if it does not already exist"
mkdir -p ".git/hooks"
if [ ! -f $OUTFILE ]; then
    echo "Creating .git/hooks/pre-commit file"
    echo "#! /usr/bin/env bash" >> $OUTFILE
    echo "# style checking per Python's PEP8 documentation" >> $OUTFILE
    echo "git diff --cached | pep8 --diff" >> $OUTFILE
fi

echo "Marking .git/hooks/pre-commit as executable"
chmod +x $OUTFILE
