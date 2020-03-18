import re
from shutil import copyfile


def create(filename):
    with open(filename) as f:
        lines = f.readlines()

    lines = list(filter(lambda x: not re.match(r'^\s*$', x), lines))
    lines = [list(line.strip('\n')) for line in lines]

    rows = len(lines)
    cols = len(lines[0])
    maze = lines

    starts = []
    for i in range(rows):
        for j in range(cols):
            if maze[i][j] == "P":
                starts.append((i, j))

    for s in starts:
        temp_filename = filename + "(" + str(s[0]) + ", " + str(s[1]) + ")"
        copyfile(filename, temp_filename)
        print("Successful create maps for worker " + str(s) + "!")




