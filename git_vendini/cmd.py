#!/usr/bin/env python
from __future__ import print_function

COPYRIGHT = """\
Copyright (C) 2011-2012 OpenStack LLC.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied.
See the License for the specific language governing permissions and
limitations under the License."""

import argparse
import os
import pkg_resources
from sh import git
import sys

def get_version():
    requirement = pkg_resources.Requirement.parse('git-vendini')
    provider = pkg_resources.get_provider(requirement)
    return provider.version

def git_directories():
    """Determine (absolute git work directory path, .git subdirectory path)."""
    out = git("rev-parse", "--show-toplevel", "--git-dir")
    return out.splitlines()

def _main():
    usage = "git vendini [OPTIONS] ... [SUBCOMMAND]"

    parser = argparse.ArgumentParser(usage=usage, description=COPYRIGHT)

    parser.add_argument("-n", "--dry-run", dest="dry", action="store_true",
                        help="Don't actually submit the branch for review")
    parser.add_argument("-r", "--remote", dest="remote",
                        help="git remote to use for gerrit")

    parser.add_argument("-l", "--list", dest="list", action="store_true",
                        help="List available reviews for the current project")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        help="Output more information about what's going on")
    parser.add_argument("--license", dest="license", action="store_true",
                        help="Print the license and exit")
    parser.add_argument("--version", action="version",
                        version='%s version %s' %
                        (os.path.split(sys.argv[0])[-1], get_version()))
    parser.add_argument("subcommand", nargs="?")

    parser.set_defaults(dry=False,
                        verbose=False,
                        list=False)
    try:
        (top_dir, git_dir) = git_directories()
    except ValueError as no_git_dir:
        pass
    else:
        no_git_dir = False
        parser.set_defaults(remote=None)
    options = parser.parse_args()
    if no_git_dir:
        raise no_git_dir

    if options.license:
        print(COPYRIGHT)
        sys.exit(0)

    print("subcommand is %s" % options.subcommand)
    sys.exit(0)

    global VERBOSE
    global UPDATE
    VERBOSE = options.verbose
    UPDATE = options.update
    remote = options.remote
    status = 0

    if options.list:
        list_reviews(remote)
        return

    ref = "publish"

    cmd = "git push %s HEAD:refs/%s/%s" % (remote, ref, branch)


    if options.dry:
        print("Please use the following command "
              "to send your commits to review:\n")
        print("\t%s\n" % cmd)
    else:
        (status, output) = run_command_status(cmd)
        print(output)

    sys.exit(status)


def main():
    try:
        _main()
    except Exception as e:
        # If one does unguarded print(e) here, in certain locales the implicit
        # str(e) blows up with familiar "UnicodeEncodeError ... ordinal not in
        # range(128)". See rhbz#1058167.
        try:
            u = unicode(e)
        except NameError:
            # Python 3, we're home free.
            print(e)
        else:
            print(u.encode('utf-8'))
        #sys.exit(e.EXIT_CODE)


if __name__ == "__main__":
    main()
