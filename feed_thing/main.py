import os
from mastodon import Mastodon

from feed_thing.settings import CLIENT_FILE, APP_NAME, URL, USERNAME_AS_EMAIL, PASSWORD
from feed_thing.tweet_info import get_timeline, get_preexisting_timeline_info
from feed_thing.user_info import inital_load_users, get_preexisting_user_info

RELOAD = False
if not os.path.exists(CLIENT_FILE):
    Mastodon.create_app(
         APP_NAME,
         api_base_url = URL,
         to_file =CLIENT_FILE
    )
if RELOAD:
    mastodon = Mastodon(
        client_id = CLIENT_FILE,
        api_base_url = URL
    )
    some_token = mastodon.log_in(
        USERNAME_AS_EMAIL,
        PASSWORD,
        to_file = 'pytooter_usercred.secret'
    )
    account = mastodon.account_verify_credentials()
    user_data = inital_load_users(mastodon)
    timeline_stuff = get_timeline(account, mastodon)
else:
    user_data = get_preexisting_user_info()
    timeline_stuff = get_preexisting_timeline_info()

friends_ids = user_data.friends_ids
followers_ids = user_data.followers_ids
with open("ashtml.html", "w", encoding="utf-8") as file:
    file.write("""
<html><style>.grey {
  padding: 20px;
  background-color: WhiteSmoke;
}</style><body>""")
    file.write(f"<table>")
    for thing in timeline_stuff.tweets:
        if thing["reblog"] is not None:
            continue

        if thing["account"]["username"] in (
                "lucid00", # posts retweets that aren't reblogs, with  ♲
        ):
            continue
        # First clause might be redunant.
        count = 0

        if thing["account"]["id"] in friends_ids and thing["account"]["id"] in followers_ids:
            # print(thing["account"]["username"] + ": " + thing["content"])
            username = thing["account"]["username"]
            content = thing["content"]
            print("Y", end="")
            account = thing['account']

            file.write("<tr>")
            file.write("<td width='50px' valign=top>")
            file.write(f"<a href='{account['url']}'>"
                       f"<img src='{account['avatar']}' height='35' width='35'/></a>")
            color = "grey" if count % 2 == 0 else ""
            count+=1
            file.write("</td>"
                       f"<td width=800px valign=top class='{color}'>")
            file.write(f"<a href='{account['url']}'>{account['display_name']} &lt;{account['acct']}&gt;</a> "
                       f"<a href='{thing['url']}'>{thing['created_at']}</a>"
                       f"<br>")
            file.write(f"{content}")
            for tag in thing["tags"]:
                file.write(f'<a href={tag["url"]}>#{tag["name"]}<a> ' )
            if thing["tags"]:
                file.write(f'<br>')
            file.write(f"</td></tr>")
        else:
            print(".", end="") # NOPE" + thing["account"]["username"] + ": " + thing["content"])
    file.write(f"</table>")
    file.write("</body></html>")
        # print(thing)
