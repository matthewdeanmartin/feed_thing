import dataclasses
from typing import Any

import orjson as json
from mastodon import Mastodon

from feed_thing.sqlite_utils import ConnectionManager


@dataclasses.dataclass
class TimelineInfo:
    tweets: list[dict[str, Any]] = dataclasses.field(default_factory=list)
    tweets_ids: set[int] = dataclasses.field(default_factory=set)


manager = ConnectionManager(
    file_name="users.db",
    commit_every=1000,
    bulk_insert_mode=True,
    read_only=False,
    print_this=print,
)


def iterate_timeline(mastodon: Mastodon, api_generator):
    objects = []
    object_ids = []

    next_data = None
    while True:
        if not next_data:
            next_data = api_generator
            if not next_data:
                print("No more objects")
                break
        else:
            if hasattr(next_data, "_pagination_next"):
                next_data = mastodon.fetch_next(next_data._pagination_next)
            else:
                print("No more objects-- no pagination_next")
                break
        for the_object in next_data:
            print(".", end="")
            objects.append(the_object)
            object_ids.append(the_object["id"])
        manager.insert_many(
            list(zip(object_ids, (json.dumps(x) for x in objects))),
            "INSERT INTO timeline (id, data) VALUES (?, ?)",
        )
        objects = []
        object_ids = []
    return objects, object_ids


def get_timeline(account, mastodon: Mastodon) -> TimelineInfo:
    # TODO add fk for who owns this timeline
    manager.excute_nonquery(
        "CREATE TABLE IF NOT EXISTS timeline (id INTEGER, data TEXT);"
    )

    objects, object_ids = iterate_timeline(mastodon, mastodon.timeline_home())


def get_preexisting_timeline_info() -> TimelineInfo:
    db_objects = [
        (uid, json.loads(x))
        for uid, x in manager.select_sql("SElect id, data from timeline")
    ]
    user_info = TimelineInfo(
        tweets=[x[1] for x in db_objects], tweets_ids=set(x[0] for x in db_objects)
    )
    return user_info


def stupid_thread(post: dict[str, Any], mastodon: Mastodon) -> list[dict[str, Any]]:
    in_reply_to_id = post["in_reply_to_id"]
    in_reply_to_tweet = mastodon.status(post["in_reply_to_id"])
    # replies = post.
    return [in_reply_to_tweet]


def fetch_thread(post: dict[str, Any], mastodon: Mastodon) -> list[dict[str, Any]]:
    # This is so wrong.
    thread = []
    thread_tree: dict[int, list[dict[int, Any]]] = {}
    previous = mastodon.status(post["in_reply_to_id"])
    thread.append(previous)
    if previous["in_reply_to_id"]:
        previous_previous = fetch_thread(previous, mastodon)
        thread.extend(previous_previous)
    return thread
