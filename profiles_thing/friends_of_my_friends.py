from profiles_thing.auth import do_auth
from profiles_thing.ugly_templater import Templater
from profiles_thing.user_info import get_preexisting_user_info, spider_friends, inital_load_users

# This makes API Calls
API_CALLS = False
if API_CALLS:
    mastodon,some_token,account = do_auth()
    inital_load_users(mastodon)
    spider_friends(mastodon)


# Below this line, no API calls
user_data = get_preexisting_user_info()


with Templater("all_users.html") as templater:
    templater.document()
    templater.file.write(f"<table>")
    for thing in user_data.friends:
        account = thing
        if account["statuses_count"]< 500:
            continue
        if account["following_count"] < 10:
            continue
        if not "Python" in account["note"]:
            continue

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
