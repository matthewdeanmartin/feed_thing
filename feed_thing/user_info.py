import dataclasses
import orjson as json
from typing import Any, Set

from mastodon import Mastodon

from feed_thing.settings import CLIENT_FILE
from sqlite_utils import ConnectionManager

@dataclasses.dataclass
class UserInfo:
    friends:list[dict[str,Any]] = dataclasses.field(default_factory=list)
    friends_ids:set[int]= dataclasses.field(default_factory=set)
    followers:list[dict[str,Any]] = dataclasses.field(default_factory=list)
    followers_ids:set[int]= dataclasses.field(default_factory=set)

manager = ConnectionManager(
        file_name="users.db",
        commit_every=1000,
        bulk_insert_mode=True,
        read_only=False,
        print_this=print,
    )


def iterate_friends_follows(account, mastodon:Mastodon, which):
    people = []
    people_ids = []

    next_data = None
    while True:
        if not next_data:
            next_data = which(id=account.id)
            if not next_data:
                print("No more followers")
                break
        else:
            if hasattr(next_data, "_pagination_next"):
                next_data = mastodon.fetch_next(next_data._pagination_next)
            else:
                print("No more followers-- no pagination_next")
                break
        for person in next_data:
            print(".", end="")
            people.append(person)
            people_ids.append(person["id"])
    return people, people_ids


def inital_load_users(mastodon: Mastodon) -> UserInfo:

    manager.excute_nonquery("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, data TEXT);")
    manager.excute_nonquery("CREATE TABLE IF NOT EXISTS users_followers (id INTEGER PRIMARY KEY, data TEXT);")
    manager.excute_nonquery("CREATE TABLE IF NOT EXISTS users_friends (id INTEGER PRIMARY KEY, data TEXT);")

    account = mastodon.account_verify_credentials()

    # for friend in mastodon.account_following(id=account.id):
    #     friends.append(friend)
    #     friend_ids.append(friend["id"])

    friends, friend_ids= iterate_friends_follows(account, mastodon, mastodon.account_following)
    manager.insert_many(
        list(zip(friend_ids, (json.dumps(x) for x in friends))),
        "INSERT INTO users_friends (id, data) VALUES (?, ?)",
    )
    followers, follower_ids = iterate_friends_follows(account, mastodon, mastodon.account_followers)
    manager.insert_many(
        list(zip(follower_ids, (json.dumps(x) for x in followers))),
        "INSERT INTO users_followers (id, data) VALUES (?, ?)",
    )

    return get_preexisting_user_info()


def get_preexisting_user_info() -> UserInfo:
    db_friends = [(uid, json.loads(x)) for uid, x in manager.select_sql("SElect id, data from users_friends")]
    db_followers = [(uid, json.loads(x)) for uid, x in manager.select_sql("SElect id, data from users_followers")]
    user_info =  UserInfo(
        friends=[x[1] for x in db_friends],
        friends_ids=set(x[0] for x in db_friends),
        followers=[x[1] for x in db_followers],
        followers_ids=set(x[0] for x in db_followers),
    )
    return user_info

