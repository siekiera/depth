#!/usr/bin/env bash

# Usage ./git_diff <path to repo> <diff args>
# e.g. ./git_diff /some/path HEAD~5 HEAD
# or ./git_diff /some/path branch1..branch2

base_path=`pwd`
repo_path="$1"
shift

cd $repo_path

git diff --name-only "$@" | sed 's/\//./g' | grep java | sed 's/\(.*\)\.java\.\(.*\).java/\2/'

cd $base_path