# Connect to the SQLite database
import orjson.orjson
import sqlite3

conn = sqlite3.connect('tweets.db')
cursor = conn.cursor()

# Query the tweets table for tweets with the word "grafana" in the content
cursor.execute('''SELECT * FROM tweets WHERE content MATCH ?''', ('twitter',))

# Fetch the results of the query
results = cursor.fetchall()

# Iterate over the results and print the URL of each tweet
for result in results:
    tweet_id = result[0]
    user = result[1]
    status = orjson.loads(result[3])
    tweet_url = f'https://mastodon.social/@{user}/{tweet_id}'
    print(user + " " + status["content"])
    print(status["uri"])

# Close the database connection
conn.close()
