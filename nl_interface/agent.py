import random
import sys

import click

import auth
import query_processing
import search

# the pair of user credentials
# credentials = None
credentials = "default", "default"


def print_msg(msg):
    """Echo a message with the prefix Sammy>"""
    click.echo("Sammy> " + msg)


def print_failure():
    failure_responses = [
        "I'm sorry. I'm not sure what you mean.",
        "I didn't quite catch that.",
        "Hmm, I'm don't know what that means",
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

        result = auth.validate_credentials(credentials)

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
        get_query()
    else:
        print_msg("Bye bye!")


def get_query():
    """Get the query from the user and process it

    :return:
    """
    while True:
        click.echo()
        query = click.prompt(credentials[0], prompt_suffix="> ")
        click.echo()
        process_query(query)


def process_query(query):
    """Process the user query

    :param query: A string with the user query
    :return:
    """
    global credentials

    if query in ["exit", "quit", "leave"]:
        print_msg("Bye bye!")
        sys.exit()

    process_result = query_processing.process(query)
    print_msg(str(process_result))

    if process_result["extra"] is not None:
        print_msg(process_result["extra"].format(credentials[0]))

    if process_result["operation"] == query_processing.OperationType.SEARCH:
        if process_result["type"] == query_processing.MediaType.ANIME:
            search.anime_search(credentials, process_result["term"])
        elif process_result["type"] == query_processing.MediaType.MANGA:
            search.manga_search(credentials, process_result["term"])

    elif process_result["operation"] == query_processing.OperationType.UPDATE:
        pass
    elif process_result["operation"] == query_processing.OperationType.ADD:
        pass
    elif process_result["operation"] == query_processing.OperationType.DELETE:
        pass
    elif process_result["extra"] is None:
        print_failure()
