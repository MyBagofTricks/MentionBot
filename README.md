# MentionBot 0.9.1b
This is a really basic bot for searching Reddit for keywords. You can search by subreddit name (eg. 'news', 'foodhacks' or 'all'). Stored keywords are stored in a database for future reference.

# Requirements
 - python 3+ 
 - pymysql - For interacting with the database: https://github.com/PyMySQL/PyMySQL/
 - PRAW - Reddit API Wrapper. Install here: here: https://praw.readthedocs.org/en/v2.1.20/
 - MySQL or compatible database to store records.

# Setup
1. Set up a MySQL compatible database and:
  * create a database
  * create a table named 'posts' with the text columns: subid, title, link
  * create a user with full privileges to it.
2. Open 'settings.py' and enter your configuration.
3. Run Mentionbot using 'python mentionbot.py'.

# Future plans
Next will likely be a  text file support. 
