#!/usr/bin/env python
# Script:  Mentionbot
# Author:  MyBagofTricks
# Version: 0.96
# Website: http://github.com/MyBagofTricks

import logging
from time import sleep

import praw
import pymysql

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-4s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

try:
    import settings as SETS
except ImportError as err:
    logger.error("Cannot continue - {}".format(err))
    raise SystemExit
done = []

dope_title = ('\n' * 80 + '*' * 80 + """
   _____                 __  .__             __________        __
  /     \   ____   _____/  |_|__| ____   ____\______   \ _____/  |_
 /  \ /  \_/ __ \ /    \   __\  |/  _ \ /    \|    |  _//  _ \   __\\
/    Y    \  ___/|   |  \  | |  (  <_> )   |  \    |   (  <_> )  |
\____|__  /\___  >___|  /__| |__|\____/|___|  /______  /\____/|__|
        \/     \/     \/                    \/       \/
Verison 0.96

********************************************************************************

Welcome to Mentionbot! This simple bot scans Reddit for keywords, then
writes the results to a MySQL database.

    Get the latest version at: http://github.com/MyBagofTricks

Requirements:
    - python 3.5
    - pyMySQL - https://github.com/PyMySQL/PyMySQL/
    - PRAW - https://praw.readthedocs.io/en/latest/
    - MySQL compatible database with
        - database named 'mentionbot'
        - table named 'posts'
        - user created with all privileges to the table

********************************************************************************
""")


def add_post(submission):
    """Inserts submission information into a MySQL database

    submission(reddit Submission object) - data structure generated by reddit
    """
    query = pymysql.connect(
        SETS.sql['host'], SETS.sql['user'], SETS.sql['pwd'], SETS.sql['db'], charset='utf8mb4'
        )
    try:
        with query.cursor() as cursor:
            cmd = "INSERT INTO posts (subid, title, link, author, subname, created)"\
                "VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(cmd, (
                submission.id, submission.title, submission.shortlink, str(submission.author),
                str(submission.subreddit_name_prefixed), submission.created)
                )
            query.commit()
    finally:
        query.close()


def empty():
    query = pymysql.connect(
        SETS.sql['host'], SETS.sql['user'], SETS.sql['pwd'], SETS.sql['db'], charset='utf8mb4'
    )
    try:
        with query.cursor() as cursor:
            cmd = "DROP TABLE IF EXISTS posts"
            cursor.execute(cmd)
            cmd = "CREATE TABLE posts (subid text,title text,"\
                "link text, author text, subname text, created int(11))"
            cursor.execute(cmd)
            query.commit()
    finally:
        query.close()


def populate():
    query = pymysql.connect(
        SETS.sql['host'], SETS.sql['user'], SETS.sql['pwd'], SETS.sql['db'], charset='utf8mb4'
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
    logger.info("Database successfully loaded. {} post(s) already populated.\n"
                .format(len(done))
                )


def init_db():
    clear = input('Clear the database? [y/n]?: ')
    if clear in ('Y', 'y'):
        logger.info("Clearing database...")
        try:
            empty()
        except pymysql.OperationalError as err:
            logger.error("Database load failed. Exiting")
            raise SystemExit
    else:
        populate()
        logger.info(("Database was not cleared."))


def reddit_login(creds):
    """ Authenticates with reddit via OAuth2

    creds(dict) - contains the reddit client_id, client_secret, password, user_agent, user_name

    Return reddit API object"""
    try:
        reddit = praw.Reddit(
            client_id=creds['client_id'],
            client_secret=creds['client_secret'],
            password=creds['password'],
            user_agent=creds['user_agent'],
            user_name=creds['user_name'],
        )
    except praw.exceptions.ClientException as err:
        logger.error("Login error - {}".format(err))
        raise SystemExit
    return reddit
    



def main(reddit_creds, sql_creds):
    reddit = reddit_login(reddit_creds)
    init_db()
    while True:
        logger.info("Scanning {} for keyword(s)".format(SETS.conf['subs']))
        for submission in reddit.subreddit("+".join(SETS.conf['subs'])).new(limit=1000):
            try:
                has_key = any(
                    string in submission.title.lower() for string in SETS.conf['keywords'])
                if submission not in done and has_key:
                    add_post(submission)
                else:
                    pass
            except Exception as err:
                logger.error("{}".format(err))
        sleep(120)


if __name__ == '__main__':
    print(dope_title)
    main(SETS.reddit, SETS.sql)
