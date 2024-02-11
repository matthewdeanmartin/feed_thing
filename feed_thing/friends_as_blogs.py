import os
from datetime import datetime

import markdownify
from mastodon import Mastodon

from feed_thing.settings import APP_NAME, CLIENT_FILE, PASSWORD, URL, USERNAME_AS_EMAIL


def do_auth():
    if not os.path.exists(CLIENT_FILE):
        Mastodon.create_app(APP_NAME, api_base_url=URL, to_file=CLIENT_FILE)
    mastodon = Mastodon(client_id=CLIENT_FILE, api_base_url=URL)
    some_token = mastodon.log_in(
        USERNAME_AS_EMAIL, PASSWORD, to_file="pytooter_usercred.secret"
    )
    account = mastodon.account_verify_credentials()
    return mastodon, some_token, account


def get_active_users(mastodon, count=25):
    """
    Gets the `count` most recently active users from the authenticated user's feed.

    Args:
        mastodon (mastodon.Mastodon): A Mastodon object authenticated with the Mastodon API.
        count (int): The number of users to retrieve.

    Returns:
        list: A list of dicts representing the most recently active users on the authenticated user's feed.
    """
    toots = mastodon.timeline_home()
    users = set([toot["account"]["id"] for toot in toots if  not  toot.get("reblog")])
    users = [mastodon.account(u) for u in users]
    users.sort(key=lambda u: u["last_status_at"], reverse=True)
    return users


def get_top_toots_for_user(mastodon, user, count=25):
    """
    Gets the `count` top toots for a given user.

    Args:
        mastodon (mastodon.Mastodon): A Mastodon object authenticated with the Mastodon API.
        user (dict): A dictionary representing a Mastodon user.
        count (int): The number of toots to retrieve.

    Returns:
        list: A list of dicts representing the top toots for the given user.
    """
    toots = mastodon.account_statuses(user["id"], exclude_replies=True)
    toots = [toot for toot in toots if  not toot.get("reblog")]
    return toots


def write_toots_to_file(mastodon, users, folder):
    """
    Writes the top toots for each user to separate markdown files.

    Args:
        mastodon (mastodon.Mastodon): A Mastodon object authenticated with the Mastodon API.
        users (list): A list of dicts representing Mastodon users.
        folder (str): The folder to write the markdown files to.
    """
    for user in users:
        toots = get_top_toots_for_user(mastodon, user)
        if not toots:
            print(f"No tweets for {user['username']}")
            continue
        filename = f"{user['username']}.md"
        file_path = os.path.join(folder, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# Top toots for {user['username']}\n\n")
            for toot in toots:
                content = markdownify.markdownify(toot["content"])
                created_at = toot["created_at"]
                f.write(f"## {created_at}\n\n{content}\n")


if __name__ == "__main__":
    # Authenticate with Mastodon
    mastodon, access_token, account = do_auth()

    # Get the active users from the feed
    active_users = get_active_users(mastodon)

    # Create a folder for today's toots
    today = datetime.today().strftime("%m-%d")
    folder = os.path.join(".", today)
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Write the top toots for each user to a separate markdown file
    write_toots_to_file(mastodon, active_users, folder)