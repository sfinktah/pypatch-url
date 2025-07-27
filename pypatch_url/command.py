#!/usr/bin/env python
"""
    Wrapper around patch.py to allow command line execution and direct patching of python modules.

    Copyright: (c) 2013 Sitka Technology Group
    Author: Stryder Crown

    Available under the terms of MIT license (http://opensource.org/licenses/MIT as of 7/27/13)

    Project home: http://github.com/sitkatech/pypatch
"""

from __future__ import print_function

import sys
import argparse

import os
import traceback
import six

from . import patch as pypatch


def apply_patch(args, debug=True):
    """
    Applies the contents of a unified diff file to a python module.
    """
    if debug:
        from logging import config

        logging_config = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'simple': {
                    'format': '%(message)s'
                }
            },
            'handlers': {
                'console': {
                    'level': debug,
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple'
                }
            },
            'loggers': {
                'pypatch.patch': {
                    'handlers': ['console'],
                    'level': debug,
                    'propagate': False
                }
            }
        }

        config.dictConfig(logging_config)

    try:
        module_path = get_module_path(args.module)
    except ImportError:
        msg = "Unable to locate module '%s'. Are you sure its installed?" % args.module
        raise argparse.ArgumentTypeError(msg)

    try:
        # Check if patch_file is a URL or local file
        if args.patch_file.startswith(('http://', 'https://', 'ftp://')):
            patch_set = pypatch.fromurl(args.patch_file)
            if not patch_set:
                print("Failed to download or parse patch from URL '%s'" % args.patch_file)
                return
        else:
            if not os.path.exists(args.patch_file):
                print("Unable to locate patch file '%s'" % args.patch_file)
                return
            patch_set = pypatch.fromfile(args.patch_file)

        # Apply path stripping if specified
        if hasattr(args, 'strip') and args.strip is not None:
            strip_count = args.strip
            for patch in patch_set.items:
                if patch.source:
                    patch.source = pypatch.pathstrip(patch.source, strip_count)
                    patch.source = pypatch.xnormpath(patch.source)
                if patch.target:
                    patch.target = pypatch.pathstrip(patch.target, strip_count)
                    patch.target = pypatch.xnormpath(patch.target)

        os.chdir(module_path)
        result = patch_set.apply()

    except Exception as err:
        print("An unexpected error has occurred: %s" % err)
        traceback.print_exc()
        if hasattr(err, 'message'):
            print(err.message)
        return False
    if result:
        print("Module '%s' patched successfully!" % args.module)
        return True
    else:
        print("Unable to apply patch. Please verify the patch contents and python module.")
        return False


def get_module_path(module_name):
    """Gets the module path without importing anything. Avoids conflicts with package dependencies."""
    path = sys.path

    if six.PY2:
        import imp
        for name in module_name.split('.'):
            file_pointer, path, desc = imp.find_module(name, path)
            path = [path, ]
            if file_pointer is not None:
                file_pointer.close()

        return path[0]

    if six.PY3:
        from pathlib import Path
        import importlib.util
        spec = importlib.util.find_spec(module_name)
        if spec:
            return Path(spec.origin).parent

    raise ImportError("Did not know how to find module '%s'" % module_name)

def main():
    """Parse args and execute function"""

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Arguments for the apply action
    apply_patch_parser = subparsers.add_parser('apply', description='Apply a patch file to a python module.')

    apply_patch_parser.add_argument('patch_file',
                                    metavar='patch file',
                                    help='A unified diff/patch file to be applied to the python module.',
                                    type=str)

    apply_patch_parser.add_argument('module',
                                    metavar='python module',
                                    help='The name of the python module to be patched.',
                                    type=str)

    apply_patch_parser.add_argument('--debug',
                                    default='DEBUG',
                                    help='use debug logging',)

    apply_patch_parser.add_argument('-p', '--strip',
                                    metavar='NUM',
                                    type=int,
                                    help='Strip NUM leading components from file names.')

    apply_patch_parser.set_defaults(func=apply_patch)
    args = parser.parse_args()
    success = args.func(args, debug=args.debug.upper())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()