# todo: adicionar scripts que fazem outras funções de processamento de submissões.
from TextProcessing import *
import sqlite3
from Database import *

def walk_forest(replies, fhand):
    """A recursive function that will go start with a comment and go through all of its replies, and write the \
    contents. It follows the form:
    1 - 1 - 1
        2 - 1
          - 2
        3 - 1
          - 2
          - 3
    2 - 1 ...
    Not used anymore, due to its indiscriminate nature (i.e. gets ALL the comments).
    """
    if (replies == []):
        return
    for comment in replies:
        write_body(comment, fhand)
        walk_forest(comment.replies, fhand)



def walk_forest_paths(comments, fhand, limit_list):
    """Goes through a comment forest but only writes the comments which are in the limit_list.
    Limit_list is a list containing the unique code of the comment, which begins at 1 and goes up for each
    comment on a tree. So the tree:
    1 - 1 - 1
      - 2 - 1
          - 2
      - 3 - 1
          - 2
          - 3
    2 - 1 ...

    has the comment codes:
    1 - 2 - 3
      - 4 - 5
      - 6 - 7
          - 8
          - 9
    10 - 11 ...

    It requires the global variable limit because, by the nature of the recursive function it is tedious to
    keep passing a variable like this, back and forth, so this is a more direct solution.
    Instead of this code, it could be possible to use the comment_id, but it is less human-readable, so manually
    selecting which comments one wants to include would get much more tedious.
    """
    if comments == []:
        return

    global comment_identifier
    comment_identifier += 1  # limit_list always starts at 1.
    global parsed_comments

    # print('Debug: ParseForesLimited, identifier', comment_identifier)

    # for comment in comments:
    #     if comment_identifier not in limit_list:
    #         continue
    #     WriteBody(comment, fhand)
    #     ParseForestLimited(comment.replies, fhand, limit_list)
    for comment in comments:
        if (comment_identifier in limit_list) and (comment_identifier not in parsed_comments):
            # print('Debug: Comment identifier:', comv mment_identifier, 'Limit list', limit_list)
            write_body(comment.body, comment.author.name, comment.author_flair_text,
                       comment.depth, fhand)
            parsed_comments.append(comment_identifier)
            # print('Debug: Parsed', comment_identifier, 'parsed comments: ', parsed_comments)
            # ParseForestLimited(comment.replies, fhand, limit_list)
        walk_forest_paths(comment.replies, fhand, limit_list)


