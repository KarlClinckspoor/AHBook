# -*- coding: utf-8 -*-
"""
Created on Sat Aug  5 10:23:26 2017

@author: Karl
"""

import re
import pypandoc

def BoldLatex (string): #sucesso
    pattern = '\*\*.*\*\*'
    match = re.search(pattern,string)
    if not match:
        #print('Debug: No bold found')
        return string
    internal = string[match.start()+2:match.end()-2]
    inlatex = '\\\\textbf{'+internal+'}'
    return re.sub(pattern,inlatex,string)

def ItalicLatex (string): #sucesso
    pattern = '[]\*(?!\*).*[^*]\*(?!\*)'
    match = re.search(pattern, string)
    if not match:
        #print('Debug: No italic found')
        return string
    internal = string[match.start()+1:match.end()-1]
    inlatex = '\\\\textit{'+internal+'}'
    return re.sub(pattern,inlatex,string)

def BulletList (string): #itemize, no latex
    pattern = '^\* '
    match = re.search(pattern, string)
    if not match:
        #print('Debug: No list found')
        return string
    internal = string[match.start()+1:]
    inlatex = '\\\\item '+internal
    return re.sub(pattern,inlatex,string)

#%%
textbold = "\n\nthis is not bold **this is supposed to be bold** and this is not bold either\n"
textitalic = "\n I hope that answers your question. If you want sources I can give you some but for the linguistic stuff it won't be in English. There's almost no English-language research on Jiāngdōng. I've certainly never seen it in all my years of working in this field. Bāshǔ has a *little* bit, but still basically none.\n The core "
textbulletlist = "\n* firstitem\n\n* seconditem\n\n* thirditem\n"

textbigger = '\n## Why does Min Chinese descend from Old Chinese rather than Middle Chinese?\n'
textquote = "\nthe details. I'll come back to this specific question near the end.\n> in the rest of China, there were surely other dialects descending from Old Chinese, but were replaced by Middle Chinese, which gives the other modern Chinese dialects.\nThis is "

textsuperscript = "^1 ^- ^Not ^a ^great ^article ^but ^that's ^sorta ^what ^there ^is ^that's ^readily ^available ^in ^English. ^Much ^more ^has ^been ^written ^in ^Mandarin."
textstrikethrough = "\nblablablablabla ~~text~~blbablabla"
textcode = "\n    blablabla\n    blablabla\n" #
textnumberedlist = "\n1.testingtestingtesting\n\n2.moretests\n\n3.finaltests\n"

texthyperlink = "(I've taken many of the theory of technology points from [Hodder 2013](http://www.amazon.com/Entangled-Archaeology-Relationships-between-Humans/dp/0470672129/ref=sr_1_1?s=books&ie=UTF8&qid=1360179315&sr=1-1&keywords=entangled+ian+hodder)):"

listofformats = [textbold, textbigger, textquote, textitalic, textsuperscript, textstrikethrough, textcode, textnumberedlist, textbulletlist]

textall = textbold+textitalic+textbulletlist+textbigger+textquote+textsuperscript+textstrikethrough+textcode+textnumberedlist
#%%
#Sucesso!
match = re.search('\*\*.*\*\*',textbold)
internalbold = textbold[match.start()+2:match.end()-2]
boldlatex = 'textit{'+internalbold+'}'
boldfinal = re.sub('\*\*.*\*\*',boldlatex,textbold)

#%% Testando num arquivo real

fhand_orig = open('WikiAfricaTest.txt','r')
fhand_replaces = open('WikiAfricaTextRep.tex','w')

for line in fhand_orig:
    line = BulletList(line)
    line = BoldLatex(line)
    line = ItalicLatex(line)
    fhand_replaces.write(line)

fhand_orig.close()
fhand_replaces.close()


#%% Testando pypandoc
fhand = open('WikiAfricaTest.txt','r')
fhand_dest = open('WikiAfricaText_Test.tex','w')
text = fhand.read()
convertedtext = pypandoc.convert_text(text,"tex",format="markdown")
fhand_dest.write(convertedtext)

#%% Testando Bold

print(BoldLatex(textall))
for item in listofformats:
    print(BoldLatex(item))

#%% Testando itálico

print(ItalicLatex(textitalic))
print(ItalicLatex(textbold))
print('-----------------')
print(ItalicLatex(textall))
print('-------------------------')
for item in listofformats:
    print(ItalicLatex(item))

#%% Testando lista

textbulletlist = "\n* firstitem\n\n* seconditem\n\n* thirditem\n"
print(BulletList(textbulletlist))
#print(BulletList(textbold))
#print(BulletList(textitalic))
    
#%% Todos os padrões
print(re.search('\*\*.*\*\*',textbold)) #acha corretamente
print(re.search('\*(?!\*).*[^*]\*(?!\*)',textitalic)) #achou italico correto, mas não o bold, nem o bullet.
print(re.search('^\*',textbulletlist)) #acha, mas só se a string não começar com \n.
print(re.search('\n\*',textbulletlist)) #acha, mas só se for precedido por \n

print(re.search('\n##',textbigger))
print(re.search('^##',textbigger))
print(re.search('^>', textquote))
print(re.search('\n>', textquote))

print(re.search('\^\S',textsuperscript))
print(re.search('~~.+~~',textstrikethrough))
print(re.search('\n    ',textcode)) #achou, mas não funciona com ^porque ele não considera o \n como sendo uma nova linha. Teremos que ver no programa em si se ele consegue reconhecer.
print(re.search('^    ',textcode))
print(re.search('\n[0-9]\.',textnumberedlist))

#%% Padrões que funcionam com os itens aqui

print(re.search('\*\*.*\*\*',textall)) #acha corretamente
print(re.search('\*(?!\*).*[^*]\*(?!\*)',textall)) #achou italico correto, mas não o bold, nem o bullet.
print(re.search('\n\*',textall)) #acha, mas só se for precedido por \n

print(re.search('\n##',textall))
print(re.search('\n>', textall))

print(re.search('\^\S',textall))
print(re.search('~~.+~~',textall))
print(re.search('\n    ',textall)) #achou, mas não funciona com ^porque ele não considera o \n como sendo uma nova linha. Teremos que ver no programa em si se ele consegue reconhecer.
print(re.search('\n[0-9]\.',textall))
