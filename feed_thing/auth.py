import os
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
