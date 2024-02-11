from feed_thing.tweet_info import get_preexisting_timeline_info
from feed_thing.ugly_templater import Templater
from feed_thing.user_info import get_preexisting_user_info

user_data = get_preexisting_user_info()
timeline_stuff = get_preexisting_timeline_info()

accounts_in_feed = {}
for thing in user_data.friends:
    account = thing
    if (
        account["id"] in user_data.friends_ids
        or account["id"] in user_data.followers_ids
    ):
        continue
    accounts_in_feed["@" + account["username"]] = account

if not accounts_in_feed:
    raise Exception("No accounts in feed")

for uid, data in accounts_in_feed.items():

    print(data)


with Templater("users.html") as templater:
    templater.document()
    templater.file.write(f"<table>")
    for thing in accounts_in_feed:
        account = accounts_in_feed[thing]
        templater.file.write("<tr>")
        templater.file.write("<td width='50px' valign=top>")
        templater.file.write(
            f"""<a href="{account["url"]}"><img src="{account["avatar"]}" width="50px" height="50px"></a>"""
        )
        templater.file.write("</td>")
        templater.file.write("<td valign=top>")
        templater.file.write(
            f"""<a href="{account["url"]}">{account["display_name"]}</a><br>"""
        )
        templater.file.write(
            f"""followers {account["followers_count"]} following {account["following_count"]}"""
        )
        templater.file.write(f"""statuses {account["statuses_count"]}""")
        templater.file.write("</td>")
        templater.file.write("<td valign=top>")
        templater.file.write(f"""{account["note"]}""")
        templater.file.write("</td>")
        templater.file.write("</tr>")
    templater.file.write(f"</table>")
