import argparse

from feed_thing.auth import do_auth


def split_toots(markdown):
    return markdown.split("\n#\n")


def toot_thread(mastodon, toots, limit=500):
    reply_to_id = None
    for toot in toots:
        content = toot[:limit]
        toot_dict = mastodon.status_post(content, in_reply_to_id=reply_to_id)
        reply_to_id = toot_dict["id"]
        print(f"Tooted: {content}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Toot a thread of toots from a markdown file.")
    parser.add_argument("filename", help="The filename of the markdown file to toot.")
    args = parser.parse_args()

    # Authenticate with Mastodon
    mastodon, access_token, account = do_auth()

    # Read in the markdown file
    with open(args.filename, "r", encoding="utf-8") as f:
        markdown = f.read()

    # Split the markdown into separate toots
    toots = split_toots(markdown)

    # Toot the thread
    toot_thread(mastodon, toots)
