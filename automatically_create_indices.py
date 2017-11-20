import Authentication as Auth
import regex as re
import glob
import time


def attribute_keys(comments):
    global key
    if comments == []:
        return

    key += 1
    for comment in comments:
        key_attributions[comment.id] = key
        attribute_keys(comment.replies)


def check_foreign_language(string):
    #Greek = re.compile('\p{Greek}')
    #Cyrillic = re.compile('\p{Cyrillic}]{1,100}')
    #Hebrew = re.compile('[\p{Hebrew}]{1,100}')
    #Arabic = re.compile('[\p{Arabic}]{1,100}')
    #Jap1 = re.compile('[\p{Han}\p{Katakana}\p{Hiragana}]{1,100}')
    #Jap2 = re.compile('[\p{Katakana}]{1,100}')
    #Jap3 = re.compile('[\p{Hiragana}]{1,100}')
    #Korean = re.compile('[\p{Korean}]{1,100}')
    #Chinese = re.compile('[\p{Han}]{1,100}')

    languages = ['Greek', 'Cyrillic', 'Hebrew', 'Arabic', 'Han', 'Hiragana', 'Katakana', 'Hangul', 'Devanagari', 'Tamil']
    languages_regexes = [r'\p{' + item + '}' for item in languages]

    patterns = {}

    for l, r in zip(languages, languages_regexes):
        patterns[l] = r

    #languages = [Greek, Cyrillic, Hebrew, Arabic, Jap1, Korean, Chinese]

    foreign_languages = ''
    # present_languages = []

    for key, item in patterns.items():
        if re.search(item, string):
            foreign_languages = foreign_languages + key
            #present_languages.append(key)

    return foreign_languages


# todo: Think about doing some 'statistics' on a submission and then select the 'cream of the crop'.
# Or perhaps just get the 10 largest comments, and then fill in the rest.
# todo: In case no comments get selected, select the longest one.
def get_good_comment_ids(comments):
    global good_ids
    global interesting_ids
    global foreign_lang
    global comment_lengths

    MAX_COMMENTS = 10
    MAX_DEPTH = 8
    MIN_SCORE = 0
    MIN_LENGTH = 1500

    if comments == []:
        return

    for comment in comments:
        comment_lengths[key_attributions[comment.id]] = len(comment.body)
        if len(interesting_ids) > MAX_COMMENTS:
            break
        if comment.depth > MAX_DEPTH:
            continue
        if (comment.score > MIN_SCORE) and (len(comment.body) > MIN_LENGTH):
            good_ids.append(
                (comment.id, key_attributions[comment.id], comment.score, comment.depth, len(comment.body)))
            interesting_ids.append((comment.id, key_attributions[comment.id], comment.score, comment.depth,
                                   len(comment.body)))
            foreign_lang.append(check_foreign_language(comment.body))

            # Checks if there is a continuous line from the present comment to the root comment. If not, populates it.
            temp_comment = comment
            for item in good_ids:
                if temp_comment.is_root:
                    break
                while temp_comment.parent().id not in item:
                    good_ids.append(
                        (temp_comment.parent().id, key_attributions[temp_comment.parent().id],
                         temp_comment.parent().score,
                         temp_comment.parent().depth, len(temp_comment.parent().body)))
                    temp_comment = temp_comment.parent()
                    if temp_comment.is_root:
                        break

        get_good_comment_ids(comment.replies)


files = glob.glob('*.txt')
#files = files[9:]
#links = open('antiquity links.txt', 'r')


reddit = Auth.CreateReddit()

for file in files:
    links = open(file, 'r')
    dest = open(file[:-4] + '_auto.txt', 'w')
    dest_full = open(file[:-4] + '_full_auto.txt', 'w')
    print('Parsing file', file)
    for link in links:
        print('Parsing link', link)
        good_ids = []  # comment ids with interesting content + the "links" between them.
        interesting_ids = []  # comment ids with interesting content.
        key_attributions = {}
        comment_lengths = {}
        key = 0
        foreign_lang = []

        if link.startswith('#'):
            dest.write(link)
            continue
        link = link.rstrip()
        submission = reddit.submission(url=link)
        comments = submission.comments
        submission.comments.replace_more(limit=0)

        attribute_keys(comments)
        get_good_comment_ids(comments)

        good_ids2 = list(set(good_ids))
        good_ids2.sort(key = lambda item: item[1])
        
        if len(comment_lengths) == 0:
            print('Submission', link, 'has no comments!')
            continue
        
        dest_full.write(submission.id + ' ' + str(good_ids2) + '\n')
        dest.write(link + ' ')
        for item in good_ids2:
            dest.write(str(item[1]) + ',')  #item[0]: comment.id, item[1]: comment key
        if len(good_ids2) == 0:  # If it didn't find anything good enough
            #dest.write('1,')  # Supposes the first comment is good.
            try:
                temp = max(comment_lengths, key = lambda x: comment_lengths[x])
                dest.write(str(temp) + ',')
            except:
                print("You're not supposed to see this.")
        dest.write(' ')
        for lang in set(foreign_lang):
            dest.write(lang + ' ')
        dest.write('\n')
    links.close()
    dest.close()
    dest_full.close()
    time.sleep(2)

# text = 'https://www.reddit.com/r/AskHistorians/comments/21fotl/what_was_an_englishman_doing_in_zimbabwe_1632/cgcmmeh?context=3 1,2,3,4,5'
# link, keys = text.split(' ')
#
# reddit = Auth.CreateReddit()
#
# submission = reddit.submission(url=link)
# comments = submission.comments
# submission.comments.replace_more(limit=0)
#
# sub_id = submission.id_from_url(link)
# sub_title = submission.title
#
# good_ids = []
# key_attributions = {}
# key = 0
#
# attribute_keys(comments)
#
# get_good_comment_ids(comments)
# #print(good_ids)
# # removes duplicates and reorders list
# good_ids2 = list(set(good_ids))
# good_ids2.sort(key = lambda item: item[1])
# print(good_ids2)

"""
    
key = 0
stats.write(sub_id + ';')
get_lengths(comments, stats, keys)
stats.write('\n')
#temp_ordered_dict = OD()
#statistics_selected_comments(comments, keys)
#summ[counter] = {'url':url, 'stats': temp_ordered_dict}
#counter += 1
"""


"""
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
"""