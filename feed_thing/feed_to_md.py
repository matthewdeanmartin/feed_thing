import os
from datetime import datetime
from markdownify import markdownify

from mastodon import Mastodon
from tqdm import tqdm

from feed_thing.auth import do_auth
from feed_thing.settings import APP_NAME, CLIENT_FILE, PASSWORD, URL, USERNAME_AS_EMAIL

# GLOBALS
mastodon, access_token, account = do_auth()

# Function to create folder if it doesn't exist
def ensure_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


# Function to get the root id of a toot
def get_root_id(toot):
    while toot["in_reply_to_id"]:
        toot = mastodon.status(toot["in_reply_to_id"])
    return toot["id"]


def run():
    # Authenticate with Mastodon


    # Get the current user's toots
    toots = mastodon.account_statuses(account["id"], exclude_replies=False)

    # Iterate through the toots
    for toot in tqdm(toots):
        # Get the root id and date of the toot
        root_id = get_root_id(toot)
        root_toot = mastodon.status(root_id)
        # root_date = datetime.strptime(root_toot["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m")
        root_date = root_toot["created_at"].strftime("%Y-%m")

        # Create the folder for this month's toots
        folder_path = f"toots/{root_date}"
        ensure_folder(folder_path)
        html_folder_path = f"html_toots/{root_date}"
        ensure_folder(html_folder_path)

        if toot["reblog"]:
            continue

        # Get the content of the toot
        html_text = toot["content"]
        if not html_text:
            print("No content for toot", toot["id"])
        markdown_text = markdownify(html_text)
        # Create the file path for this toot
        segment = f"toot_{root_id}_{toot['id']}_{root_date}"
        file_path = f"{folder_path}/{segment}.md"
        html_path = f"{html_folder_path}/{segment}.html"

        # Write the content to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_text)

if __name__ == '__main__':
    run()