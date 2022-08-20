"""
This is the main command line interface for the eco_validate package.
"""

import argparse

import eco_validate.summarize.cli as summarize

def main():

    descr = "eco_validate is a package designed to help test and summarize the results of multiple repeated EcoTyper runs."
    parser = argparse.ArgumentParser(description=descr)
    subparsers = parser.add_subparsers()

    summarize.setup(subparsers)

    args = parser.parse_args()
    args.func( args )