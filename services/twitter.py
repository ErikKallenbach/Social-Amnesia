from datetime import datetime
from tkinter import messagebox

import sys
sys.path.insert(0, "../utils")
from utils import helpers

import arrow
import tweepy

# for dev purposes
# from secrets import twitter_consumer_key, twitter_consumer_secret, twitter_access_token, twitter_access_token_secret

# twitter state object
# Handles configuration options set by the user
twitter_state = {}

# neccesary global bool for the scheduler
already_ran_bool = False

def set_twitter_login(consumer_key, consumer_secret, access_token, access_token_secret, login_confirm_text):
    """
    Logs into twitter using tweepy, gives user an error on failure
    :param consumer_key: input received from the UI
    :param consumer_secret: input received from the UI
    :param access_token: input received from the UI
    :param access: input received from the UI
    :param login_confirm_text: confirmation text - shown to the user in the UI
    :return: none
    """
    # ============ REAL =============
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    # ============= REAL ============

    # =========== DEV TESTING =============
    # auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    # auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    # ============== DEV TESTING ==============

    api = tweepy.API(auth)

    twitter_username = api.me().screen_name

    login_confirm_text.set(f'Logged in to twitter as {twitter_username}')

    # initialize state
    twitter_state['api'] = api
    twitter_state['time_to_save'] = arrow.utcnow().replace(hours=0)
    twitter_state['max_favorites'] = 0
    twitter_state['max_retweets'] = 0
    twitter_state['test_run'] = 1


def set_twitter_time_to_save(hours_to_save, days_to_save, weeks_to_save, years_to_save, current_time_to_save):
    """
    See set_time_to_save function in helpers.py
    """
    twitter_state['time_to_save'] = helpers.set_time_to_save(hours_to_save, days_to_save, weeks_to_save, years_to_save, current_time_to_save)


def set_twitter_max_favorites(max_favorites, current_max_favorites):
    """
    See set_max_score function in helpers.py
    """
    twitter_state['max_favorites'] = helpers.set_max_score(max_favorites, current_max_favorites, 'favorites')


def set_twitter_max_retweets(max_retweets, current_max_retweets):
    """
    See set_max_score function in helpers.py
    """
    twitter_state['max_retweets'] = helpers.set_max_score(max_retweets, current_max_retweets, 'retweets')


def gather_items(item_getter):
    """
    Keeps making calls to twitter to gather all the items the API can
    index and build an array of them
    :param item_getter: the function call being made to twitter to get tweets or favorites from the user's account
    :return user_items: an array of the items gathered
    """
    user_items = []
    new_items = item_getter(count=200)
    user_items.extend(new_items)
    oldest = user_items[-1].id - 1

    while len(new_items) > 0:
        new_items = item_getter(count=200, max_id=oldest)
        user_items.extend(new_items)
        oldest = user_items[-1].id - 1

    return user_items


def delete_twitter_tweets(root, currently_deleting_text, deletion_progress_bar, num_deleted_items_text):
    """
    Deletes user's tweets according to user configurations.
    :param root: the reference to the actual tkinter GUI window
    :param currently_deleting_text: Describes the item that is currently being deleted.
    :param deletion_progress_bar: updates as the items are looped through
    :param num_deleted_items_text: updates as X out of Y comments are looped through
    :return: none
    """
    user_tweets = gather_items(twitter_state['api'].user_timeline)
    total_tweets = len(user_tweets)

    num_deleted_items_text.set(f'0/{str(total_tweets)} items processed so far')

    count = 1
    for tweet in user_tweets:
        tweet_snippet = tweet.text[0:50]
        if len(tweet.text) > 50:
            tweet_snippet = tweet_snippet + '...'
        for char in tweet_snippet:
            # tkinter can't handle certain unicode characters,
            #  so we strip them
            if (ord(char) > 65535):
                tweet_snippet = tweet_snippet.replace(char, '')

        time_created = arrow.Arrow.fromdatetime(tweet.created_at)

        if (time_created > twitter_state['time_to_save']):
            currently_deleting_text.set(f'Tweet: `{tweet_snippet}` is more recent than cutoff, skipping.')
        elif (tweet.favorite_count >= twitter_state['max_favorites']):
            currently_deleting_text.set(
                f'Tweet: `{tweet_snippet}` has more favorites than max favorites, skipping.')
        elif (tweet.retweet_count >= twitter_state['max_retweets'] and not tweet.retweeted):
            currently_deleting_text.set(
                f'Tweet: `{tweet_snippet}` has more retweets than max retweets, skipping.')
        else:
            if (twitter_state['test_run'] == 0):
                currently_deleting_text.set(f'Deleting tweet: `{tweet_snippet}`')

                twitter_state['api'].destroy_status(tweet.id)
            else:
                currently_deleting_text.set(f'-TEST RUN- Would delete tweet: `{tweet_snippet}`')

        num_deleted_items_text.set(f'{str(count)}/{str(total_tweets)} items processed.')
        deletion_progress_bar['value'] = round((count / total_tweets) * 100, 1)

        root.update()

        count += 1


def delete_twitter_favorites(root, currently_deleting_text, deletion_progress_bar, num_deleted_items_text):
    """
    Deletes users's favorites according to user configurations.
    :param root: the reference to the actual tkinter GUI window
    :param currently_deleting_text: Describes the item that is currently being deleted.
    :param deletion_progress_bar: updates as the items are looped through
    :param num_deleted_items_text: updates as X out of Y comments are looped through
    :return: none
    """
    user_favorites = gather_items(twitter_state['api'].favorites)
    total_favorites = len(user_favorites)

    num_deleted_items_text.set(f'0/{str(total_favorites)} items processed so far')

    count = 1
    for favorite in user_favorites:
        favorite_snippet = favorite.text[0:50]
        if len(favorite.text) > 50:
            favorite_snippet = favorite_snippet + '...'
        for char in favorite_snippet:
            # tkinter can't handle certain unicode characters,
            #  so we strip them
            if ord(char) > 65535:
                favorite_snippet = favorite_snippet.replace(char, '')

        currently_deleting_text.set(f'Deleting favorite: `{favorite_snippet}`')

        time_created = arrow.Arrow.fromdatetime(favorite.created_at)

        if time_created > twitter_state['time_to_save']:
            currently_deleting_text.set(f'Favorite: `{favorite_snippet}` is more recent than cutoff, skipping.')
        else:
            if (twitter_state['test_run'] == 0):
                currently_deleting_text.set(f'Deleting favorite: `{favorite_snippet}`')
                twitter_state['api'].destroy_favorite(favorite.id)
            else:
                currently_deleting_text.set(f'-TEST RUN- Would remove favorite: `{favorite_snippet}`')

        num_deleted_items_text.set(
            f'{str(count)}/{str(total_favorites)} items processed.')
        deletion_progress_bar['value'] = round((count / total_favorites) * 100, 1)

        root.update()

        count += 1


def set_twitter_test_run(test_run_bool):
    """
    Set whether to run a test run or not (stored in state)
    :param test_run_bool: 0 for real run, 1 for test run
    :return: none
    """
    twitter_state['test_run'] = test_run_bool.get()


def set_twitter_scheduler(root, scheduler_bool, hour_of_day, string_var, progress_var):
    """
    The scheduler that users can use to have social amnesia wipe 
    tweets/favorites at a set point in time, repeatedly.
    :param root: tkinkter window
    :param scheduler_bool: true if set to run, false otherwise
    :param hour_of_day: int 0-23, sets hour of day to run on
    :param string_var, progress_var - empty Vars needed to run the deletion functions
    :return: none
    """
    global already_ran_bool
    if not scheduler_bool.get():
        already_ran_bool = False
        return

    current_time = datetime.now().time().hour

    if current_time == hour_of_day and not already_ran_bool:
        messagebox.showinfo(
            'Scheduler', 'Social Amnesia is now erasing your past on twitter.')

        delete_twitter_tweets(root, string_var, progress_var, string_var)
        delete_twitter_favorites(root, string_var, progress_var, string_var)

        already_ran_bool = True
    if current_time < 23 and current_time == hour_of_day + 1:
        already_ran_bool = False
    elif current_time == 0:
        already_ran_bool = False

    root.after(1000, lambda: set_twitter_scheduler(
        root, scheduler_bool, hour_of_day, string_var, progress_var))
