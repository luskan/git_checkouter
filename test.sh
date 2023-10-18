#!/bin/bash

rm -rf test_repositories

mkdir test_repositories
cd test_repositories

# Create and setup repo1
mkdir repo1
cd repo1
git init
echo "This is a file in repo1" > file1.txt
git add file1.txt
git commit -m "Initial commit in repo1"
echo "More content for file in repo1" >> file1.txt
git add file1.txt
git commit -m "Second commit in repo1"
cd ..

# Create and setup repo2
mkdir repo2
cd repo2
git init
echo "This is a file in repo2" > file2.txt
git add file2.txt
git commit -m "Initial commit in repo2"
echo "More content for file in repo2" >> file2.txt
git add file2.txt
git commit -m "Second commit in repo2"
cd ..

cd ..

./venv/bin/python3 ./git_checkouter.py --path ./test_repositories --date "09:26:2023 23:00" --timediff 30
./venv/bin/python3 ./git_checkouter.py --path ./test_repositories --date "09:26:2023 23:00" --prefix my_branch_
./venv/bin/python3 ./git_checkouter.py --path ./test_repositories --date "09:26:2023 23:00" --prefix my_branch_ --ignore-repos repo1
