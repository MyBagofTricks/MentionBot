#!/usr/bin/env python
# Script:  Mentionbot
# Author:  MyBagofTricks
# Version: 0.95a
# Website: http://github.com/MyBagofTricks

# Importing standard modules
import sys
import signal
from time import sleep, localtime, strftime
# Try loading third party modules and folders
try:
    import praw
    import pymysql
    from modules import messages as msg
    import settings as sets
except Exception as e:
    print ("[x] Error: {}".format(e))
    sys.exit()
done = []


def addpost(subid, title, link, author, subname, created, sql):
    done.append(subid)
    msg.print_add(link, title)
    if sql:
        query = pymysql.connect(sets.db['host'], sets.db['user'],
                                sets.db['pwd'], sets.db['db'],
                                charset='utf8')
        cursor = query.cursor()
        cmd = "INSERT INTO posts (subid, title, link, author, subname, date) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(
            cmd, (subid, title, link, author, subname, created))
        query.commit()
        query.close()
    else:
        pass    # Exists to handle debug mode where db isn't present


def empty():
    clear = input('[-] Clear the database? [y/n]?: ')
    if clear in ('y', 'Y', 'yes', 'YES', 'Yes'):
        msg.print_clear()
        query = pymysql.connect(sets.db['host'], sets.db['user'],
                                sets.db['pwd'], sets.db['db'],
                                charset='utf8')
        cursor = query.cursor()
        cmd = "DELETE FROM posts"
        cursor.execute(cmd)
        query.commit()
        query.close()
    else:
        msg.print_not_clear()


def populate():
    query = pymysql.connect(sets.db['host'], sets.db['user'],
                            sets.db['pwd'], sets.db['db'],
                            charset='utf8')
    cursor = query.cursor()
    cmd = "SELECT * FROM posts"
    cursor.execute(cmd)
    results = cursor.fetchall()
    for row in results:
        subid = row[0]
        done.append(subid)
    query.close()
    msg.print_loaded(len(done))


def init_db():
    try:
        empty()
        populate()
        return True
    except pymysql.OperationalError as e:
        msg.error_nosql(e)
        return False


def handle_sigint(signum, frame):       # handles CTRL-C exiting
    msg.error_exit()
    sys.exit()


def main():

    msg.print_title()
    signal.signal(signal.SIGINT, handle_sigint)
    usesql = init_db()
    r = praw.Reddit(sets.r_login['agent'])
    try:
        r.login(
            sets.r_login['user'], sets.r_login['pwd'], disable_warning=True)
    except (praw.errors.InvalidUserPass, praw.errors.InvalidUser) as e:
        print ("Login error: {}".format(e))

    while True:
        for cur_sub in sets.subs:
            msg.run_msg(strftime("%a, %y-%m-%d %H:%M:%S %Z ", localtime()),
                        cur_sub)
            subreddit = r.get_subreddit(cur_sub)
            try:
                for sub in subreddit.get_new(limit=1000):
                    title_text = sub.selftext.title()
                    has_key = any(
                        string in title_text.lower() for string in sets.keywords)
                    if sub.id not in done and has_key:
                        if sub.author.name is False:
                            sub.author.name = "Deleted"
                        addpost(sub.id, sub.title, sub.short_link,
                                sub.author.name, str(sub.subreddit),
                                sub.created, usesql)
                    else:
                        pass
            except Exception as e:
                msg.error_gen(e)
        sleep(sets.time_sleep)

if __name__ == '__main__':
    main()
