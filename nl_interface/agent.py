import random
import sys

import click

import add
import auth
import delete
import query_processing
import search
import ui

# the pair of user credentials
credentials = "default", "default"


def print_msg(msg):
    """Echo a message with the prefix Sammy>"""
    click.echo("Sammy> " + msg)


def print_failure():
    failure_responses = [
        "I'm sorry. I'm not sure what you mean.",
        "I didn't quite catch that.",
        "Hmm, I'm don't know what that means.",
        "Lol, wut?"
    ]
    print_msg(random.choice(failure_responses))


def authorise_user():
    """Get a pair of credentials from the user

    :return: True is authenticated, False if their was an error and user quit
    """
    global credentials
    while True:
        credentials = auth.get_user_credentials("Please enter your username", "And now your password")

        result = ui.threaded_action(auth.validate_credentials, "Authenticating", **{"credentials": credentials})

        if result is not auth.StatusCode.SUCCESS:
            if result == auth.StatusCode.CONNECTION_ERROR:
                print_msg("Oh no, there was an error connecting to MAL. Maybe check your internet connection")
            elif result == auth.StatusCode.UNAUTHORISED:
                print_msg("Something was wrong with the username or password :(")
            elif result == auth.StatusCode.OTHER_ERROR:
                print_msg("Some kind of error has occurred :'(")

            if click.confirm("Sammy> Do you want to try again?"):
                continue
            else:
                return False

        return True


def welcome():
    """Print out the welcome message and bootstrap program functionality"""
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
    """Process the user query

    :param query: A string with the user query
    """
    global credentials

    if query.lower() in ["exit", "quit", "leave", "bye"]:
        print_msg("Bye bye!")
        sys.exit()

    process_result = query_processing.process(query)
    print_msg(str(process_result))

    if process_result["extra"] is not None:
        print_msg(process_result["extra"].format(credentials[0]))

    # search queries
    if process_result["operation"] == query_processing.OperationType.SEARCH:
        if process_result["type"] == query_processing.MediaType.ANIME:
            search.search(credentials, "anime", process_result["term"])
        elif process_result["type"] == query_processing.MediaType.MANGA:
            search.search(credentials, "manga", process_result["term"])

    # update queries
    elif process_result["operation"] == query_processing.OperationType.UPDATE:
        pass

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

    # if the system failed to understand the query
    elif process_result["extra"] is None:
        print_failure()
