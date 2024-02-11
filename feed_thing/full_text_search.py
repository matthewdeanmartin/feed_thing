import orjson

import os

from mastodon import Mastodon
import sqlite3
from feed_thing.auth import do_auth
from feed_thing.settings import APP_NAME, CLIENT_FILE, URL

if not os.path.exists(CLIENT_FILE):
    Mastodon.create_app(APP_NAME, api_base_url=URL, to_file=CLIENT_FILE)
mastodon, some_token, user_account = do_auth()

def run():
    # Connect to the SQLite database
    with  sqlite3.connect('tweets.db') as conn:
        cursor =conn.cursor()
        # Create a table to store the tweets using the FTS4 full-text index feature
        cursor.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS tweets USING fts4 (id INTEGER PRIMARY KEY, user TEXT, content TEXT, json TEXT)''')

        loop_over(cursor)
        cursor.close()
        # Commit the changes to the database
        conn.commit()


def loop_over(cursor):
    # Fetch the list of accounts that you follow
    following = mastodon.account_following(id=user_account.id)

    # Iterate over each account and download their tweets
    i = 0
    for account in following:
        # Fetch the user's statuses
        statuses = mastodon.account_statuses(account['id'])

        # Iterate over each status and insert it into the database
        for status in statuses:
            cursor.execute('''INSERT INTO tweets (id, user, content, json) VALUES (?, ?, ?, ?)''',
                           (status['id'], status['account']['username'], status['content'], orjson.dumps(status)))
            i += 1
            if i > 50:
                return

if __name__ == '__main__':
    run()