from datetime import datetime

from feed_thing.auth import do_auth

# Get your own user id
mastodon, token, account = do_auth()
user_id = account["id"]

# Get your own timeline for the past 3 months
now = datetime.now()
three_months_ago = now.replace(month=now.month-3)
timeline = mastodon.account_statuses(user_id,since=three_months_ago)

# Find tweet storms (two or more self-replies) and print their root ids
tweet_storms = []
for status in timeline:
    if status["in_reply_to_account_id"] == user_id: # A self-reply
        if status["in_reply_to_id"] in tweet_storms: # Already part of a tweet storm
            continue # Skip this one
        else: # A new tweet storm
            root_id = status["in_reply_to_id"] # The id of the first tweet in the storm
            tweet_storms.append(root_id) # Add it to the list

print("Tweet storms found:")
for root_id in tweet_storms:
    print(root_id)