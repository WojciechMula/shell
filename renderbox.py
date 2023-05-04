#!/usr/bin/env python3

import sys
import argparse

def main():
    args = parse_args()
    draw(args.fields)


def draw(fields):
    drawaux(fields, '┌', '┬', '┐', lambda s: '─' * len(s))
    drawaux(fields, '│', '│', '│', lambda s: s)
    drawaux(fields, '└', '┴', '┘', lambda s: '─' * len(s))


def drawaux(fields, start, middle, end, value):
    for i, s in enumerate(fields):
        if i == 0:
            print(start, end='')
        else:
            print(middle, end='')
        print(value(s), end='')
    else:
        print(end)


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-w", "--width",
                    type=int)
    ap.add_argument("-c", "--count",
                    type=int)
    ap.add_argument("fields",
                    nargs='+')

    args = ap.parse_args()
    if args.count is None:
        args.count = len(args.fields)

    if args.width is not None:
        for i in range(len(args.fields)):
            args.fields[i] = '%*s' % (args.width, args.fields[i])

    while args.count > len(args.fields):
        if args.width is None:
            args.fields.append('')
        else:
            args.fields.append(' ' * args.width)

    return args


if __name__ == '__main__':
    main()
