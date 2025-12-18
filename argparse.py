##chapitre 6

import sys

original_path = sys.path

sys.path = sys.path[1:]

import argparse as ap

sys.path = original_path

def parse():
    parser = ap.ArgumentParser(add_help=False)
    parser.add_argument('-courte', action='store_true')
    parser.add_argument('-longue', action='store_true')
    parser.add_argument('-help', action='store_true')
    args = parser.parse_args()
    return args

def process_args(args):
    if args.help:
        print("flag: -courte, -longue, -help")
    if args.courte:
        exit(0)
    if args.longue:
        exit(0)
    else:
        exit(84)

if __name__ == '__main__':
    args = parse()
    process_args(args)
    