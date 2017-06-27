#!/usr/bin/env python
# Script:  Mentionbot
# Author:  MyBagofTricks
# Version: 0.96
# Website: http://github.com/MyBagofTricks

from time import sleep, localtime, strftime
import logging

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


def add_post(subid, title, link, author, subname, created, sql):
    query = pymysql.connect(
        SETS.sql['host'], SETS.sql['user'], SETS.sql['pwd'], SETS.sql['db'],charset='utf8mb4'
    )
    try:
        with query.cursor() as cursor:
            cmd = "INSERT INTO posts (subid, title, link, author, subname, created)"\
                "VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(cmd, (subid, title, link, author, subname, created))
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
            logger.warning(
                "Database load failed. Running without database - data will not be persistent"
            )
            return False
    else:
        populate()
        logger.info(("Database was not cleared."))


def main():
    try:
        reddit = praw.Reddit(
            client_id=SETS.reddit['client_id'],
            client_secret=SETS.reddit['client_secret'],
            password=SETS.reddit['password'],
            user_agent=SETS.reddit['user_agent'],
            user_name=SETS.reddit['user_name'],
        )
    except praw.exceptions.ClientException as err:
        logger.error("Login error - {}".format(err))
        raise SystemExit
    print(dope_title)
    init_db()
    while True:
        logger.info("Scanning {} for keyword(s)".format(SETS.conf['subs']))
        for submission in reddit.subreddit("+".join(SETS.conf['subs'])).new(limit=1000):
            name = str(submission.author)
            subname = str(submission.subreddit_name_prefixed)
            try:
                has_key = any(
                    string in submission.title.lower() for string in SETS.conf['keywords'])
                if submission not in done and has_key:
                    add_post(
                        submission.id, submission.title, submission.shortlink,
                        str(submission.author), str(submission.subreddit_name_prefixed), submission.created, True)
                else:
                    pass
            except Exception as err:
                logger.error("{}".format(err))
        sleep(SETS.conf['sleep'])


if __name__ == '__main__':
    main()
