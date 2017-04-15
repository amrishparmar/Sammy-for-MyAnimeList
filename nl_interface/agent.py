import random
import sys

import click

import add
import auth
import delete
import network
import query_processing
import search
import update

# the pair of user credentials
credentials = "default", "default"


def print_msg(msg):
    """Echo a message with the prefix Sammy>"""
    click.echo("Sammy> " + msg)


def print_failure():
    """Print out a failure response chosen at random"""
    failure_responses = [
        "I'm sorry. I'm not sure what you mean.",
        "I didn't quite catch that.",
        "Hmm, I'm don't know what that means.",
        "I'm not entirely sure I know what it is you want.",
        "I don't quite understand what you mean.",
        "I'm sure not sure I understand."
    ]
    print_msg(random.choice(failure_responses))


def print_connection_error_msg():
    print_msg("Oh no, there was an error connecting to MAL. Please check your internet connection")


def authorise_user():
    """Get a pair of credentials from the user

    :return: True is authenticated, False if their was an error and user quit
    """
    global credentials
    while True:
        credentials = auth.get_user_credentials("Please enter your username", "And now your password")

        result = auth.validate_credentials(credentials)

        if result is not network.StatusCode.SUCCESS:
            if result == network.StatusCode.CONNECTION_ERROR:
                print_connection_error_msg()
            elif result == network.StatusCode.UNAUTHORISED:
                print_msg("Something was wrong with the username or password :(")
            elif result == network.StatusCode.OTHER_ERROR:
                print_msg("Some kind of error has occurred :'(")

            if click.confirm("Sammy> Do you want to try again?"):
                continue
            else:
                return False

        return True


def welcome():
    """Print out the welcome message and bootstrap program functionality
    
    :return: True if the user authenticated successfully, False otherwise
    """
    click.clear()
    click.echo("====== MAL Natural Language Interface ======")
    click.echo()
    print_msg("Hello! My name is Sammy and I am your MyAnimeList digital assistant.")
    print_msg("Before we get started, I need you to confirm your MAL account details.")
    click.echo()

    if authorise_user():
        click.echo()
        print_msg("Yay, everything checked out! Let's get started.")
        print_msg("What can I do for you today?")
        return True
    else:
        print_msg("Bye bye!")
        return False


def get_query():
    """Get the query from the user and process it"""
    while True:
        click.echo()
        query = click.prompt(credentials[0], prompt_suffix="> ")
        click.echo()
        process_query(query)


def process_query(query):
    """Process the user query and carry out the requested action

    :param query: A string, the raw user query
    """
    process_result = query_processing.process(query)
    print_msg(str(process_result)) # print out the dictionary for debug purposes

    if process_result == query_processing.Extras.EXIT:
        print_msg("Bye bye!")
        sys.exit()

    if process_result["extra"] == query_processing.Extras.GREETING:
        greetings = ["Hi", "Hello", "Yo"]
        print_msg("{}, {}".format(random.choice(greetings), credentials[0]))
    elif process_result["extra"] == query_processing.Extras.THANKS:
        thanks = ["No problem", "You're welcome", "Any time", "You are very welcome"]
        print_msg("{} :D".format(random.choice(thanks)))

    # search queries
    if process_result["operation"] == query_processing.OperationType.SEARCH:
        if process_result["type"] == query_processing.MediaType.ANIME:
            search.search(credentials, "anime", process_result["term"])

        elif process_result["type"] == query_processing.MediaType.MANGA:
            search.search(credentials, "manga", process_result["term"])

    # update queries
    elif process_result["operation"] == query_processing.OperationType.UPDATE:
        if process_result["type"] == query_processing.MediaType.ANIME:
            if process_result["modifier"] == query_processing.UpdateModifier.STATUS:
                if process_result["value"] == query_processing.StatusType.WATCHING:
                    update.update_anime_list_entry(credentials, "status", process_result["term"], 1)
                elif process_result["value"] == query_processing.StatusType.COMPLETED:
                    update.update_anime_list_entry(credentials, "status", process_result["term"], 2)
                elif process_result["value"] == query_processing.StatusType.ON_HOLD:
                    update.update_anime_list_entry(credentials, "status", process_result["term"], 3)
                elif process_result["value"] == query_processing.StatusType.DROPPED:
                    update.update_anime_list_entry(credentials, "status", process_result["term"], 4)
                elif process_result["value"] == query_processing.StatusType.PLAN_TO_WATCH:
                    update.update_anime_list_entry(credentials, "status", process_result["term"], 6)

            elif process_result["modifier"] == query_processing.UpdateModifier.SCORE:
                if process_result["value"] is None:
                    print_msg("I'm sorry, but the new score value must be between 1 and 10.")
                else:
                    update.update_anime_list_entry(credentials, "score", process_result["term"],
                                                   process_result["value"])

            elif process_result["modifier"] == query_processing.UpdateModifier.EPISODE:
                pass

            elif process_result["modifier"] == query_processing.UpdateModifier.CHAPTER:
                pass

            elif process_result["modifier"] == query_processing.UpdateModifier.VOLUME:
                pass

        elif process_result["type"] == query_processing.MediaType.MANGA:
            if process_result["modifier"] == query_processing.UpdateModifier.STATUS:
                if process_result["value"] == query_processing.StatusType.READING:
                    update.update_manga_list_entry(credentials, "status", process_result["term"], 1)
                elif process_result["value"] == query_processing.StatusType.COMPLETED:
                    update.update_manga_list_entry(credentials, "status", process_result["term"], 2)
                elif process_result["value"] == query_processing.StatusType.ON_HOLD:
                    update.update_manga_list_entry(credentials, "status", process_result["term"], 3)
                elif process_result["value"] == query_processing.StatusType.DROPPED:
                    update.update_manga_list_entry(credentials, "status", process_result["term"], 4)
                elif process_result["value"] == query_processing.StatusType.PLAN_TO_READ:
                    update.update_manga_list_entry(credentials, "status", process_result["term"], 6)

            elif process_result["modifier"] == query_processing.UpdateModifier.SCORE:
                if process_result["value"] is None:
                    print_msg("I'm sorry, but the new score value must be between 1 and 10.")
                else:
                    update.update_manga_list_entry(credentials, "score", process_result["term"],
                                                   process_result["value"])

            elif process_result["modifier"] == query_processing.UpdateModifier.EPISODE:
                pass

            elif process_result["modifier"] == query_processing.UpdateModifier.CHAPTER:
                pass

            elif process_result["modifier"] == query_processing.UpdateModifier.VOLUME:
                pass

    elif process_result["operation"] == query_processing.OperationType.UPDATE_INCREMENT:
        if process_result["type"] == query_processing.MediaType.ANIME:
            update.update_anime_list_entry(credentials, "episode", process_result["term"])

        elif process_result["type"] == query_processing.MediaType.MANGA:
            if process_result["modifier"] == query_processing.UpdateModifier.CHAPTER:
                update.update_manga_list_entry(credentials, "chapter", process_result["term"])

            elif process_result["modifier"] == query_processing.UpdateModifier.VOLUME:
                update.update_manga_list_entry(credentials, "volume", process_result["term"])

    # add queries
    elif process_result["operation"] == query_processing.OperationType.ADD:
        if process_result["type"] == query_processing.MediaType.ANIME:
            add.add_entry(credentials, "anime", process_result["term"])

        elif process_result["type"] == query_processing.MediaType.MANGA:
            add.add_entry(credentials, "manga", process_result["term"])

    # delete queries
    elif process_result["operation"] == query_processing.OperationType.DELETE:
        if process_result["type"] == query_processing.MediaType.ANIME:
            delete.delete_entry(credentials, "anime", process_result["term"])

        elif process_result["type"] == query_processing.MediaType.MANGA:
            delete.delete_entry(credentials, "manga", process_result["term"])

    elif process_result["operation"] == query_processing.OperationType.VIEW_LIST:
        if process_result["type"] == query_processing.MediaType.ANIME:
            update.view_list(credentials[0], "anime")

        elif process_result["type"] == query_processing.MediaType.MANGA:
            update.view_list(credentials[0], "manga")

    # if the system failed to understand the query
    elif process_result["extra"]:
        print_failure()
