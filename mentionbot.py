#!/usr/bin/env python
# Script:  Mentionbot
# Author:  MyBagofTricks
# Version: 0.95
# Website: http://github.com/MyBagofTricks

import signal
from time import sleep, localtime, strftime

try:
    import praw
    import pymysql
    import pymysql.cursors
    from modules import messages as msg
    import settings as sets
except ImportError as err:
    print ("[x] Error: {}".format(err))
    raise SystemExit
done = []


def addpost(subid, title, link, author, subname, created, sql):
    query = pymysql.connect(
        sets.db['host'], sets.db['user'],
        sets.db['pwd'], sets.db['db'],
        charset='utf8'
    )
    try:
        with query.cursor() as cursor:
            cmd = "INSERT INTO posts (subid, title, link, author, subname, created)"\
            "VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(cmd, (subid, title, link, author, subname, created))
            query.commit()
    finally:
        query.close()

def createtable():
    query = pymysql.connect(
        sets.db['host'], sets.db['user'],
        sets.db['pwd'], sets.db['db'],
        charset='utf8'
    )
    try:
        with query.cursor() as cursor:
            cmd = "CREATE TABLE posts (subid text,title text,"\
            "link text, author text, subname text, created int(11))"
            cursor.execute(cmd)
    finally:
        query.close()
    return True


def empty():
    query = pymysql.connect(
        sets.db['host'], sets.db['user'],
        sets.db['pwd'], sets.db['db'],
        charset='utf8'
    )
    try:
        with query.cursor() as cursor:
            cmd = "DROP TABLE IF EXISTS posts"
            cursor.execute(cmd)
            query.commit()
    finally:
        query.close()


def populate():
    query = pymysql.connect(
        sets.db['host'], sets.db['user'],
        sets.db['pwd'], sets.db['db'],
        charset='utf8'
    )
    try:
        with query.cursor() as cursor:
            cmd = "SELECT subid FROM posts"
            cursor.execute(cmd)
            result = cursor.fetchall()
            for row in result:
                done.append(row[0])
    finally:
        query.close()
    msg.print_loaded(len(done))



def init_db():
    clear = input('[-] Clear the database? [y/n]?: ')
    if clear in ('Y', 'y'):
        msg.print_clear()
        try:
            empty()
            createtable()
        except pymysql.OperationalError as err:
            msg.error_nosql(err)
            return False
    else:
        populate()
        msg.print_not_clear()


def handle_sigint(signum, frame):       # handles CTRL-C exiting
    msg.error_exit()
    raise SystemExit


def main():
    try:
        reddit = praw.Reddit(
            client_id=sets.r_login['client_id'],
            client_secret=sets.r_login['client_secret'],
            password=sets.r_login['password'],
            user_agent=sets.r_login['user_agent'],
            user_name=sets.r_login['user_name'],
    )
    except praw.exceptions.ClientException as err:
        print("[x] Login error  - {err}".format(err=err))
        raise SystemExit
    signal.signal(signal.SIGINT, handle_sigint)
    msg.print_title()
    usesql = init_db()
    while True:
        for cur_sub in sets.subs:
            msg.run_msg(strftime("%a, %y-%m-%d %H:%M:%S %Z ", localtime()),
                        cur_sub)
            try:
                for submission in reddit.subreddit('/all').new(limit=1000):
                    title_text = submission.title
                    has_key = any(
                        string in title_text.lower() for string in sets.keywords)
                    if submission not in done and has_key:
                        if submission.author is False:
                            submission.author = "Deleted"
                        addpost(submission.id, submission.title, submission.shortlink,
                                'submission.author', submission.display_name,
                                submission.created, True)
                    else:
                        pass
            except Exception as e:
                msg.error_gen(e)
        sleep(sets.time_sleep)

if __name__ == '__main__':
    main()
