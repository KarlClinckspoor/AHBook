# -*- coding: utf-8 -*-
"""
Created on Sun Aug  6 11:50:16 2017

@author: Karl
"""

import pypandoc
import os
import Parsing_submission_pandoc as Parse
import Authentication as Rauth
from praw.models import MoreComments
#import datetime

currentdir = os.getcwd()
filedir = os.path.join(currentdir,('WikiAfricaTest.txt'))


reddit = Rauth.CreateReddit()
submission = reddit.submission(url='https://www.reddit.com/r/AskHistorians/comments/2ba2ah/i_have_read_that_the_colonization_of_zimbabwe/cj3azuc')
comments = submission.comments
submission.comments.replace_more(limit=0)

fhead = open('pandoc_header4.tex','w')
#fbody = open('pandoc_body2.tex','w')

Parse.WriteHeadP(submission,fhead)
Parse.WriteBodyP(comments[0],fhead)
#pypandoc.convert_file(filedir, 'latex', format='markdown', extra_args=('--wrap=preserve'), encoding='utf-8', outputfile='directtest.tex', filters=None)

fhead.close()
#fbody.close()

'''
#works, generates a file without the extra headers
#pypandoc.convert_file(filedir, 'latex', format='markdown', outputfile='wikitest4.tex')

commtext1 = "This is a topic that comes up very often on this subreddit, so in anticipation I've prepared a response in advance to throw down before the conversation devolves into a heated debate about the strengths/weaknesses of *Guns, Germs and Steel* (which is where this discussion usually goes). I apologize in advance, because this is going to be a full essay, but it's something that I feel has never really been explained adequately here. Before I answer this question directly I need to give a few caveats regarding the current understanding that anthropologists and archaeologists have regarding American Indian technology and how technology works in general (I've taken many of the theory of technology points from [Hodder 2013](http://www.amazon.com/Entangled-Archaeology-Relationships-between-Humans/dp/0470672129/ref=sr_1_1?s=books&ie=UTF8&qid=1360179315&sr=1-1&keywords=entangled+ian+hodder)):\n"

commtext2 = "* **1: Pre-Columbian American Indian cultures were not as culturally and technologically different from their counterparts in Eurasia as most people seem to think:** A lot of people seem to think all American Indians were nomadic hunter-gatherers chasing the buffalo. In fact, there were regions of the Americas that had long traditions of urban civilization and were more densely populated than most areas of Europe and Asia. The Inca empire had a highway system with supply stations at regular intervals that connected most of the major cities in their two-million-square-kilometer empire. The Aztec empire's capital city of Tenochtitlan had an elaborate system of aqueducts and canals that distributed potable water throughout the city and moved waste products out into the agricultural fields. Yes, there were large swaths of the Americas where only hunter-gatherers lived, but the same was true for Eurasia (i.e., the Central Asian Steppes).\n"

commtext3 = "* **2: In the long view of history, it's fairly remarkable that two cultures not in contact with each other would share *any* technology in common:** Anatomically modern humans have existed for 200,000 years. Yet, within a few thousand years of each other, American Indians and Eurasians separately invented agriculture, cities, state governments, pottery, writing, bows and arrows, plaster, aqueducts, and a slew of other inventions. In my opinion, the similarities are more remarkable than the differences.\n"

commtext4 = commtext1+'\n'+commtext2+'\n'+commtext3

#latextext1 = pypandoc.convert_text(commtext1, 'latex', format='markdown')
#latextext2 = pypandoc.convert_text(commtext2, 'latex', format='markdown')
#latextext3 = pypandoc.convert_text(commtext3, 'latex', format='markdown')
latextext4 = pypandoc.convert_text(commtext4, 'latex', format='markdown')
#latextext5 = latextext1+latextext2+latextext3

print(latextext4)
'''