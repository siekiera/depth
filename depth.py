#!/usr/bin/env python3
import argparse
import sys

from typing import Dict, List, Set

# Allow only packages from a given codebase, so that it wouldn't infinitely dwell into unwanted classes
PREFIXES_ALLOW_RECURSION = []
PREFIXES_STOP_RECURSION = []
# These will not be available as straight dependencies, so need some hassle around
FOLLOW_IMPL_CLASSES = True
IMPL_SUFFIXES = ['Impl', 'Implementation']
DEBUG = False


def main():
    dep_mapping = parse_mapping()
    files_to_look_for = get_files_to_look_for()

    recursive_usage_find(dep_mapping, files_to_look_for)


def parse_mapping() -> Dict[str, List[str]]:
    dep_mapping = {}
    # expects input like
    # full.package.SomeClass -> other.package.SomeClassItDependsOn .
    for line in sys.stdin:
        try:
            (source, dependency) = line.replace("->", " ").split()[:2]
            if dependency not in dep_mapping:
                dep_mapping[dependency] = []
            dep_mapping[dependency].append(source)

            # For a scenario where you have e.g. interface SomeService and SomeServiceImpl and Impl is never called directly,
            # but e.g. by reflection
            # Mapping is SomeServiceImpl -> SomeService, we write it inverted, so that it wouldn't stop at impl but go further to
            # interface usages
            if FOLLOW_IMPL_CLASSES and is_impl_dependency(source, dependency):
                if source not in dep_mapping:
                    dep_mapping[source] = []
                dep_mapping[source].append(dependency)
        except ValueError:
            pass

    return dep_mapping


def is_impl_dependency(source: str, dependency: str) -> bool:
    source_simple = get_simple_name(source)
    dep_simple = get_simple_name(dependency)
    return any(source_simple == dep_simple + suffix for suffix in IMPL_SUFFIXES)


def get_simple_name(full_cls_name: str) -> str:
    return full_cls_name.split('.')[-1]


def get_files_to_look_for() -> List[str]:
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('classes_to_look_for', type=str, nargs='+',
                        help='class names to look for')
    parser.add_argument('--debug', dest='debug', action="store_true",
                        help='turn on verbose debug printlns')
    parser.add_argument('--prefixes-allow-recursion', dest='prefixes_allow', nargs='*',
                        help='package prefixes, for which recursion is allowed', type=str)
    parser.add_argument('--prefixes-stop-recursion', dest='prefixes_stop', nargs='+',
                        help='package prefixes, for which recursion is stopped.',
                        type=str)
    args = parser.parse_args()
    # TODO: implement some cleaner way than global variables
    global DEBUG
    DEBUG = args.debug
    global PREFIXES_STOP_RECURSION, PREFIXES_ALLOW_RECURSION
    if args.prefixes_allow:
        PREFIXES_ALLOW_RECURSION = args.prefixes_allow
    if args.prefixes_stop:
        PREFIXES_STOP_RECURSION = args.prefixes_stop
    return args.classes_to_look_for


def recursive_usage_find(dep_mapping: Dict[str, List[str]], files_to_look_for: List[str], already_visited: Set[str] = None):
    if already_visited is None:
        already_visited = set()
    for file_to_look_for in files_to_look_for:

        # Prevent infinite recursion due to circular dependencies
        if file_to_look_for in already_visited:
            debug("stopping recursion due to circular dependency, class: " + file_to_look_for)
            continue
        already_visited.add(file_to_look_for)

        # Allow only packages from our codebase, so that it wouldn't infinitely dwell into e.g. java or ext. dependency classes
        if is_allowed_to_dig_deeper(file_to_look_for):
            debug("checking " + file_to_look_for)
            if file_to_look_for in dep_mapping:
                usages_of_dependency = dep_mapping[file_to_look_for]
                # Recursive search
                recursive_usage_find(dep_mapping, usages_of_dependency, already_visited)
            else:
                # Found leaf - print to std out, can be read by another script
                debug("found leaf: " + file_to_look_for)
                print(file_to_look_for)


def is_allowed_to_dig_deeper(source: str) -> bool:
    return (not PREFIXES_ALLOW_RECURSION or any(source.startswith(prefix) for prefix in PREFIXES_ALLOW_RECURSION)) \
           and all(not source.startswith(prefix) for prefix in PREFIXES_STOP_RECURSION)


def debug(something):
    if DEBUG:
        print("debug: ", something, file=sys.stderr)


if __name__ == '__main__':
    main()
