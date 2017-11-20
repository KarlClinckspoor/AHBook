# -*- coding: utf-8 -*-

from pylatex import Document, Section, Subsection, Command
from pylatex.utils import italic, NoEscape
import Authentication as Rauth
from praw.models import MoreComments
import datetime

reddit = Rauth.CreateReddit()

submission = reddit.submission(url='https://www.reddit.com/r/AskHistorians/comments/393j58/why_does_min_chinese_descend_from_old_chinese/')
comments = submission.comments
submission.comments.replace_more(limit=0)
date = datetime.datetime.fromtimestamp(submission.created_utc)
firstcomment = comments[0]
firstreply = comments[0].replies[0]
#secondcomment = comments[1]


doc = Document('article')
doc.preamble.append(Command('title','Asia'))
doc.append(NoEscape('\maketitle'))
#doc.append(Command('maketitle))

doc.create(Section(submission.title))
doc.append(submission.selftext)

doc.create(Section(firstcomment.author.name+'\textit{',firstcomment.author_flair_text+'}'))
doc.append(firstcomment.body)
doc.append(Command('textit',firstreply.body))
#doc.create(Section(secondcomment.author.name+Command('textit',firstcomment.author_flair_text)))
doc.generate_tex('teste.tex')

'''
 |      Examples
 |      --------
 |      >>> Command('documentclass',
 |      >>>         options=Options('12pt', 'a4paper', 'twoside'),
 |      >>>         arguments='article').dumps()
 |      '\\documentclass[12pt,a4paper,twoside]{article}'
 |      >>> Command('com')
 |      '\\com'
 |      >>> Command('com', 'first')
 |      '\\com{first}'
 |      >>> Command('com', 'first', 'option')
 |      '\\com[option]{first}'
 |      >>> Command('com', 'first', 'option', 'second')
 |      '\\com{first}[option]{second}'
 '''