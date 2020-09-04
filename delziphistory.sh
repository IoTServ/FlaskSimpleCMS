#!/bin/bash
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch app/main/views.py' --prune-empty --tag-name-filter cat -- --all
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch app/user/views.py' --prune-empty --tag-name-filter cat -- --all
git push origin master --force