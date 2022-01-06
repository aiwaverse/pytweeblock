from time import sleep
from typing import Set, Tuple, Union
from dotenv import load_dotenv
import os
import tweepy
import re
from tqdm import tqdm


class CurrentUser:
    def __init__(self, client: tweepy.Client, id: str) -> None:
        self.client: tweepy.Client = client
        self.id: str = id


class PyTweeBlockError(Exception):
    pass


def main() -> None:
    curr_user = generate_current_user()
    print(
        len(
            generate_account_blocklist(
                curr_user,
                "@Lavi__Laio",
            )
        )
    )


def block_users(curr: CurrentUser, blocklist: Set[str]) -> None:
    for id in tqdm(blocklist):
        curr.client.block(id)


def generate_account_blocklist(curr: CurrentUser, account: str) -> Set[str]:
    account = account.removeprefix("@")
    account: tweepy.User = curr.client.get_user(
        username=account, user_auth=True
    ).data
    users_following = collect_set_paginator(
        curr.client.get_users_followers,
        account.id,
        user_auth=True,
        max_results=1000,
    )
    users_to_not_block = collect_set_paginator(
        curr.client.get_users_followers,
        curr.id,
        user_auth=True,
        max_results=1000,
    ) | collect_set_paginator(
        curr.client.get_users_following,
        curr.id,
        user_auth=True,
        max_results=1000,
    )
    block_list = users_following - users_to_not_block
    return block_list


def generate_tweet_blocklist(curr: CurrentUser, tweet_link: str) -> Set[str]:
    account = ""
    tweet_id = ""
    try:
        account = re.findall(r"(?<=twitter\.com\/)\w+", tweet_link)[0]
        tweet_id = re.findall(r"(?<=status\/)\d+", tweet_link)[0]
    except IndexError:
        raise PyTweeBlockError(
            "Error extracting account name and tweet id from link"
        )
    account: tweepy.User = curr.client.get_user(
        username=account, user_auth=True
    ).data
    liking_users = collect_set_paginator(
        curr.client.get_liking_users,
        tweet_id,
        user_auth=True,
        max_results=1000,
    )
    retweeting_users = collect_set_paginator(
        curr.client.get_retweeters,
        tweet_id,
        user_auth=True,
        max_results=1000,
    )
    users_following = collect_set_paginator(
        curr.client.get_users_followers,
        account.id,
        user_auth=True,
        max_results=1000,
    )
    users_to_not_block = collect_set_paginator(
        curr.client.get_users_followers,
        curr.id,
        user_auth=True,
        max_results=1000,
    ) | collect_set_paginator(
        curr.client.get_users_following,
        curr.id,
        user_auth=True,
        max_results=1000,
    )
    block_list = (
        liking_users | users_following | retweeting_users
    ) - users_to_not_block
    return block_list


def collect_set_paginator(method, *args, **kwargs) -> Set[str]:
    to_return = set()
    for response in tweepy.Paginator(method, *args, **kwargs):
        to_return |= set(
            map(
                lambda user: user.id,
                response.data,
            )
        )
        print("Able to get Paginator once!")
    return to_return


def get_pin_input(url: str) -> str:
    """
    Basic while loop to get the pin from the user
    Returns the identifier stripped and only if it's only digits
    """
    while True:
        print(url)
        verifier = input("Please enter the PIN code: ")
        verifier = verifier.strip()
        if verifier.isdigit():
            return verifier
        else:
            print("Please input only the PIN code")


def generate_current_user() -> CurrentUser:
    load_dotenv()
    consumer_key = os.getenv("TWITTER_API_KEY")
    consumer_secret = os.getenv("TWITTER_API_SECRET")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    verifier = get_pin_input(auth.get_authorization_url())
    user_key, user_secret = auth.get_access_token(verifier)
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=user_key,
        access_token_secret=user_secret,
        wait_on_rate_limit=True,
    )
    user_id = tweepy.API(auth).verify_credentials().id_str
    print("Login successful!")
    return CurrentUser(client, user_id)


if __name__ == "__main__":
    main()
