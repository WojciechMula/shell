#!/usr/bin/env python3

import sys

hist = {}
max_length = 0
for line in sys.stdin:
    if line[-1] == '\n':
        line = line[:-1]

    hist[line] = hist.get(line, 0) + 1
    max_length = max(max_length, len(line))

raw = [(line, count) for line, count in hist.items()]
raw.sort(key=lambda item: item[1], reverse=True)

for line, count in raw:
    print(f"{line:{max_length}}: {count}")
