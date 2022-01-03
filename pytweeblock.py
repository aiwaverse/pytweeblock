from typing import Tuple, Union
from dotenv import load_dotenv
import os
import tweepy
import re


class CurrentUser:
    def __init__(self, client: tweepy.Client, id: str) -> None:
        self.client: tweepy.Client = client
        self.id: str = id


class PyTweeBlockError(Exception):
    pass


def main() -> None:
    curr_user = generate_current_user()
    liking_users = curr_user.get_liking_users(
        "1478011189561114629", user_auth=True
    )
    print(liking_users.data)
    print(type(liking_users.data[0]))


def block_related_to_tweet(client: tweepy.Client, tweet_link: str) -> None:
    account, tweet_id = ""
    try:
        account = re.findall(r"(?<=twitter\.com\/w+", tweet_link)[0]
        tweet_id = re.findall(r"(?<=status\/)\d+", tweet_link)[0]
    except IndexError:
        raise PyTweeBlockError(
            "Error extracting account name and tweet id from link"
        )
    account: tweepy.User = client.get_user(account).data
    liking_users = set(client.get_liking_users(tweet_id, user_auth=True))
    users_following = set(client.get_users_followers(account.id))
    users_to_not_block = set(client.get_users_followers())


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
    )
    user_id = print(tweepy.API(auth).verify_credentials().id_str)
    print("Login successful!")
    return CurrentUser(client, user_id)


if __name__ == "__main__":
    main()
