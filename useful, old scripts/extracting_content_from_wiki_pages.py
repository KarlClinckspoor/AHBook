import Authentication as Rauth
import time
import os

reddit = Rauth.CreateReddit()
wikilist = open('WikiPagesCrop.txt', 'r')
#temp_count = 0

for line in wikilist:
    line = line.rstrip()
    '''
    if temp_count >=3:
        print('Breaking temporarily')
        break
    temp_count += 1
    '''
    line_copy = line[:].replace('/','-')
    fname = 'wiki_'+line_copy+'.txt'
    currentdir = os.getcwd()
    finaldir = os.path.join(currentdir,('\\Wiki\\'+fname))
    try:
        fhand = open(finaldir, 'x', encoding='utf-8')
    except:
        print(fname,'already exists. Skipping')
        continue

    current_wiki = reddit.subreddit('AskHistorians').wiki[line]
    content = current_wiki.content_md
    fhand.write(content)
    fhand.close()
    time.sleep(4)

wikilist.close()
