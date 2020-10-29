A tool which utilizes jdeps and git diff to find leaf usages of all modified Java files.

Example usages:

Find all leaf usages of all files modified between branch1 and branch2
```
./depth.sh -d branch1..branch2 -r /path/to/git/repo
```

Find all leaf usages of all files modified in 2 last commits
```
./depth.sh -d HEAD~2..HEAD -r /path/to/git/repo
```

Find all leaf usages of `pkg.SomeClass`
```
./depth.sh -c pkg.SomeClass -r /path/to/git/repo
```

Store the jdeps result to a file
```
./depth.sh -s tmp/deps.txt -r /path/to/git/repo
```

Find all leaf usages of `pkg.SomeClass` using deps from a file
```
./depth.sh -c pkg.SomeClass -f tmp/deps.txt -r /path/to/git/repo
```