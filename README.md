# AHBook
A project designed to preserve the contents of /r/askhistorians in pdf format.

Needs a file called Authentication.py with your API codes from reddit.

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
