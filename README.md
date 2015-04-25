# MentionBot 0.9a
This is a really basic bot for searching Reddit for keywords. You can search by subreddit name (eg. 'news', 'foodhacks' or 'all'). Stored keywords are stored in a database for future reference.

# Requirements
 - python 2.7
 - pymysql - For interacting with the database: https://github.com/PyMySQL/PyMySQL/
 - PRAW - Reddit API Wrapper. Install here: here: https://praw.readthedocs.org/en/v2.1.20/
 - ConfigObj - This handles setup. Install here: http://www.voidspace.org.uk/python/configobj.html
 - MySQL or compatible database to store records.

# Setup
1. Set up a MySQL compatible database and:
  * create a database
  * create a table named 'posts' with the text columns: subid, title, link
  * create a user with full privileges to it.
2. Open 'mentionbot.setup' and enter your configuration.
3. Run it!

# Future plans
Next will likely be a migration to Python 3, fancy ACSII menus, and maybe text file support. 
