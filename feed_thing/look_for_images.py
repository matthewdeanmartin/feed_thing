"""
Using mastodon as a sort of flicker (social picture albums) or delicious (social bookmarks)
"""
from datetime import datetime

from feed_thing.auth import do_auth

# Get your own user id
mastodon, token, account = do_auth()
def print_tweets_with_images(user_id):
    # Get the user's timeline
    timeline = mastodon.account_statuses(user_id)

    # Loop through each status
    for status in timeline:
        # Check if the status has media attachments
        if status["media_attachments"]:
        # Print the image URL and text content for each attachment
            for media in status["media_attachments"]:
                print(media["url"])
                print(media["description"])
import re

def print_tweets_with_links(user_id):
    # Get the user's timeline
    timeline = mastodon.account_statuses(user_id)

    # Loop through each status
    for status in timeline:
        # Get the status content as HTML
        content = status["content"]

        # Find all hyperlinks in the content using a regex
        links = re.findall(r'<a href="(.*?)".*?>(.*?)</a>', content)

        # If there are any links, print them with their text
        if links:
            print("Links found in status:", status["id"])
            for link in links:
                print(link[0], "-", link[1])

