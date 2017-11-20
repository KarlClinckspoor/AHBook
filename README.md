# AHBook

## Objective
Transform the selected comments and questions from /r/askhistorians into a book, or several, for archival purposes.

## Pre-Requisites

1. Python 3, https://www.python.org/
2. PRAW, The Python Reddit API Wrapper. https://praw.readthedocs.io/en/latest/. This is used to access reddit data. Install it with pip.
3. pandoc, https://pandoc.org/index.html, and pypandoc. These are used to convert the data from markdown to latex.
4. A LaTeX distribution, with XeLaTeX. This is to create the book pdf itself, as the script only transforms the data into .tex files. XeLaTeX is necessary to easily have multiple languages in a single file. I'm on windows, so I use MikTeX as the LaTeX distribution and Texmaker as a convenient UI.

## Running python scripts

Install python, run 'pip praw', 'pip pypandoc' and download pandoc. To run the scripts, type 'python <script name.py>', simple as that. Most of them do not require any further input from the user. If your system is saying that it can't recognize the command 'python', try 'py', and if that still has some problems, add the python.exe folder into the PATH variable of your operating system. Use google to check how to do that.

## Authentication
Needs a file called Authentication.py with your developer API codes from reddit. You can get these codes by registering a new app on https://www.reddit.com/prefs/apps/.

Copy and paste your API codes, username and password into the code at the bottom.

    import praw

    def CreateReddit():
        client_id = 'abc'
        client_secret = 'abc'
        my_password = 'abc'
        my_username = 'abc'
        reddit = praw.Reddit(client_id=client_id,
                             client_secret = client_secret,
                             password = my_password,
                             user_agent='abc',
                             username = my_username)
        return reddit 

## How this project works

There are several scripts and files, each with a specific function, starting from an interesting submission and ending into a .pdf file. Namely, these steps are:

* Acquiring a number of interesting submissions. This can be done manually, or automatically. I opted to create a script and extract the links on the wiki files from /r/AskHistorians, as they already went through the trouble of categorizing a ton of stuff. I plan to write additional scripts to get submissions from /r/badhistory, and the submissions posted to /r/bestof and /r/DepthHub. These links have to be one at each line of a .txt file.
* Select the specific comments that are interesting. This is done by adding a single space after the link, and writing the "comment number" of every comment that is of interest, separated by commas. The "comment number" starts at 1 and is the first comment of the submission (when it's sorted by best, or top, not sure; it's PRAW's default though), and then its first response is 2, this one's first response is 3, and so on. There are two scripts to help you with that. The first creates a "summary" of all the submissions in a .txt file, with the comment number, the depth, the author and its score. The second uses a predetermined "rule" to check which comments should be selected (for example, SCORE > 1, LENGTH > 1500, DEPTH < 4), and generates a second .txt file with the links and the comments numbers.
* Go through a list of URLs, access the contents through PRAW, extract the markdown text and format it into usable .tex files.
* Create a .pdf file through XeLaTeX and correct any errors that might appear. These are, typically, few and far between at the moment. This step isn't automatic, you have to tell XeLaTeX to compile the file at the end.

Now, I will detail each step and which scripts to what.

### Acquiring links from a text file or wiki

Scripts used:
1. extracting_content_from_wiki_pages.py
2. extract_urls_from_wiki_source.py

#### extracting_content_from_wiki_pages.py

This script reads the file 'WikiPagesCrop.txt', which is just a list of all the wiki pages. It then creates files with the contents of these pages, in markdown.

In case you want a list of all wiki pages from a subreddit, run the following code:

    import Auth
    reddit = Auth.CreateReddit()
    for page in reddit.subreddit('AskHistorians').wiki:
        print(page)

Just change 'AskHistorians' to whatever subreddit name you want. The file 'WikiPagesCrop.txt' is just this text pasted into notepad.

#### extract_urls_from_wiki_pages.py

This script scans through every line of every wiki page file created by the previous script and removes all the unnecessary text, leaving only the links (which I used a regular expression to match anything containing 'comments', change it to suit your needs). Also, it leaves any markdown markers for sections, like '#', so that the .tex building script can identify when there are different sections and change accordingly.

### Selecting comments

Scripts used:

1. testing_summaries.py
2. open_urls.py
3. automatically_create_indices.py

The output list must look like this in order for the next scripts, which get the links and the comments, to work:

    https://www.reddit.com/r/AskHistorians/comments/3jzfmj/how_would_an_average_roman_citizen_travel_through/cutowr9?context=3 1,2

The numbers 1,2, etc, mean the "comment number", which is the sequence of comments from top to bottom. This comment tree:

    1 - 1 - 1
      - 2 - 1
          - 2
      - 3 - 1
          - 2
          - 3
    2 - 1 ...

has the following comment codes:

    1 - 2 - 3
      - 4 - 5
      - 6 - 7
          - 8
          - 9
    10 - 11 ...

The following scripts are useful for choosing which comments to select.

#### testing_summaries.py

This script opens the files containing a list of links (which could have been created by the previous scripts) and then goes through all of then, creating a "summary" file that has the URL and all the contents of each submission, but with only the indices, usernames, lengths, depth. Change the lines that open files to select which files you want to parse. I will write a more definite efition of this, hopefully, in the future, that selects which files you want and writes out a proper name for them.

The output file looks like this:

    https://www.reddit.com/r/AskHistorians/comments/3jzfmj/how_would_an_average_roman_citizen_travel_through/cutowr9?context=3
    3jzfmj How would an average Roman citizen travel through the Empire from one location to another?

    1 Astrogator 44 8130
    # 2 Astrogator 35 6768
    ## 3 Shaoshyant 5 117
    ### 4 Astrogator 1 24
    ## 5 thelapoubelle 2 188
    ### 6 Astrogator 1 64
    # 7 Quierochurros 2 198
    ## 8 Astrogator 3 338
    # 9 im_not_afraid 1 181
    ----
    (... next submission...)

So, it contains the URL in the first line, the submission_id and title in the second, followed by every comment, which has the depth (symbolized by the number of #; no # means depth 0), index, the username, the comment score (upvotes-downvotes) and the length. On this example, one would probably select Astrogator's comments, which are the longest. To do so, open the list of links and, beside this specific link, type the indexes, for example '1,2'. This will select the first two comments. The link line will look like this then:

    https://www.reddit.com/r/AskHistorians/comments/3jzfmj/how_would_an_average_roman_citizen_travel_through/cutowr9?context=3 1,2

It is always useful to give a cursory glance to what the contents of the submissions really are, so to save time from opening each link individually, you can use the open_urls.py script.

#### open_urls.py

This is a simple script that tells your browser to open 7 of the links on a specific file and then waits until you press enter. When you do, it opens 7 more until there are no more links on that file. To select the file, just change the string on the open command.

You are supposed to create a summary of that link list, then open a few links just to check which comments you want to include. It is useful to have a large monitor, possible two, for this step.

#### automatically_create_indices.py

Since there is a LOT of links on the /r/AskHistorians wiki (more than 3000!), it is completely infeasible to go through all of them, for a single person. Therefore, I created this script that goes through each submission and automatically selects the comments based on a few rules. At the moment, the following logic is implemented.

These variables can be set:

    MAX_COMMENTS = 10
    MAX_DEPTH = 8
    MIN_SCORE = 0
    MIN_LENGTH = 1500

MAX_COMMENTS sets the maximum number of "good" comments that can be in a submission, that is, comments that satisfy all conditions. The script "populates" the rest of the list by adding the "intermediary" comments, so that the comments have context.

MAX_DEPTH sets the maximum depth of a good comment. Useful for limiting very long discussions, especially on very popular threads. Depth starts at 0 and every subsequent child comment has a depth incremented by one.

MIN_SCORE sets the minimum score for a comment. This is to prevent tirades and rambling by laymen.

MIN_LENGTH sets the primary filter. At the moment, if a comment has more than 1500 characters, it is characterized as good. However, it is possible that newer submissions, which contain the 'askhistorians expects good, sourced comments, etc etc', might get these selected. It is necessary to filter these out. It would be interesting to create some "statistics" on a submission and select the top comments based on that.

Note that, to provide context, the script also selects intermediary comments, like follow-up questions, even if they do not obey some of these rules.

You can also change the filters in whatever way you can.

### Create .tex files from link lists

Used scripts:

1. Parsing_restricted_urls.py
2. Parsing_submission_pandoc.py

#### Parsing_restricted_urls.py

This file creates a file called 'main.tex' file by loading the preamble of 'Maintex preamble.dat', then opens the list of links with the selected comment indices, then sends this information to Parsing_submission_pandoc.py. This is the workhorse of this project, for it deals with actually going through the submissions and comments and transforming them into useful .tex files.

Each submission is saved into its own .tex file with the submission id + '.tex' as its filename. They have the preamble from the file 'subtex preamble.dat'. These are then imported into the main.tex file. Due to the preamble of the subfiles, you can also compile them individually, almost without change, you just need to uncomment a few lines.

The .dat extensions are just lazy workaround for me, they just contain plaintext, just so that glob doesn't get these files when parsing everything.

While pandoc handles the bulk of the conversion, this script still changes a few things, like properly escaping certain characters and encapsulating different scripts with the appropriate code.

If the link list contains symbols for sections in Markdown, such as '### Africa', the script generates chapters with those names.

The script waits for 2 seconds between links because it prevents a few errors. I had some submissions come out completely empty for some reason, and doing so fixes that.

### Creating PDF

Now that you have a huge bunch of .tex files, you need to compile them into a readable .pdf file. To do so, you have to run XeLaTeX on them. What I like to do is use Texmaker to open the main.tex file, then I select XeLaTeX for the upper part of the menu, then compile the file three times. This properly generates the indices and the contents. It might take a while if the list is very long.

In case there are errors, which are normally not many, you can use the logviewer of Texmaker and correct them on the .tex file itself. Normally, these are errors where pandoc inserted too many newlines, breaking up {} blocks in LaTeX, or improperly escaped characters that passed through the code. It always complains that the package 'bidi', for bidirectional text, was loaded in an improper order, but it compiles just file. I have to look into it better.

## Acknowledgements
I would like to thank the wonderful mods and flaired users in /r/askhistorians for creating such an interesting community, and my friends and family for supporting me. This is my first 'serious' programming project since I started learning Python around June 2017, through Coursera and I have learned a lot.