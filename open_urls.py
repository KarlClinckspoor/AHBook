# -*- coding: utf-8 -*-

import webbrowser

fhand = open('wiki_antiquity_parsed.txt','r')

counter = 0

for line in fhand:
    if len(line.split(' ')) == 2:
        continue
    counter += 1
    line = line.rstrip()
    webbrowser.open(line, new=2, autoraise=False)
    if counter % 7 == 0:
        input('Waiting. Please press enter to continue.')

fhand.close()
