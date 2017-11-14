import Authentication as Auth


def statistics_selected_comments(comments, selection):

    global key
    key += 1
    global temp_ordered_dict

    for comment in comments:
        if key not in selection:
            continue

        depth = comment.depth
        score = comment.score
        comment_length = len(comment.body)
        try:
            authorname = comment.author.name
        except:
            authorname = 'deleted'

        temp_ordered_dict[key] = {'depth': comment.depth, 'score': comment.score, 'length': len(comment.body)}
        statistics_selected_comments(comment.replies, selection)


def get_lengths(comments, fhand, selection):
    if comments == []:
        return
    global key
    key += 1
    for comment in comments:
        if key not in selection:
            continue

        depth = comment.depth
        score = comment.score
        try:
            authorname = comment.author.name
        except:
            authorname = 'deleted'
        comment_length = len(comment.body)

        # summ_content = '#'*depth + ' '+authorname+' '+str(comment_length)
        #summ_content = '%s %d %s %d %d\n' % ('#' * depth, key, authorname, score, comment_length)
        fhand.write(str(comment_length) + ';')
        get_lengths(comment.replies, fhand, selection)


links = open('wiki_africa_parsed.txt', 'r')
stats = open('wiki_africa_stats.txt', 'w')
stats.write('title;comment_length\n')

reddit = Auth.CreateReddit()


for link in links:
    if link.startswith('#'):
        continue
    link = link.rstrip()
    url, keys = link.split(' ')
    keys = list(map(int, keys.split(',')))
    submission = reddit.submission(url=url)
    comments = submission.comments
    submission.comments.replace_more(limit=0)

    sub_id = submission.id_from_url(link)
    sub_title = submission.title

    key = 0
    stats.write(sub_id + ';')
    get_lengths(comments, stats, keys)
    stats.write('\n')
    #temp_ordered_dict = OD()
    #statistics_selected_comments(comments, keys)
    #summ[counter] = {'url':url, 'stats': temp_ordered_dict}
    #counter += 1

stats.close()
