#!/usr/bin/env bash

base=$(pwd)

while getopts 'd:c:r:s:f:' opt; do
    case $opt in
      (d)   DIFF_ARGS+=("$OPTARG");;
      (c)   CLASSES+=("$OPTARG");;
      (r)   REPO=$OPTARG;;
      (s)   STORE_DEPS=$OPTARG;;
      (f)   DEPS_SRC=$OPTARG;;
      (*)   exit 1;;
    esac
done

shift "$OPTIND"

echo "Repo: $REPO"
echo "Jdeps store file: $STORE_DEPS"
echo "Jdeps source file $DEPS_SRC"
echo "Classes: ${CLASSES[@]}"
echo "Git diff args: ${DIFF_ARGS[@]}"

# Repo mandatory for all stuff
if [[ -z "$REPO" ]]; then
  echo "Repo required!"
  exit 1
fi

# just storing deps
if [[ ! -z "$STORE_DEPS" ]]; then
  jdeps -v "$REPO" > $STORE_DEPS
  echo "Stored to $STORE_DEPS"
  exit 0
fi

# Handle diff or classes
if [[ ! -z "$DIFF_ARGS" ]]; then
  CLASSES=$(./git_diff.sh "$REPO" "${DIFF_ARGS[@]}")
elif [ -z "$CLASSES" ]; then
  echo "Either classes or diff args have to be specified!"
  exit 1
fi

depth_cmd=( ./depth.py $CLASSES )
echo "Running ${depth_cmd[@]}"
echo "-----------------------"

# run either getting the deps from the file or running command
if [ -z "$DEPS_SRC" ]; then
  jdeps -v "$REPO" | "${depth_cmd[@]}"
else
  "${depth_cmd[@]}" < "$DEPS_SRC"
fi
