import random

import click

import add
import auth
import delete
import network
import query_processing as qp
import search
import update

# the pair of user credentials
credentials = "default", "default"


def print_msg(msg):
    """Echo a message with the prefix "Sammy>"
    
    :param msg: A string, the message to echo
    """
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
    """Print out a message corresponding to a requests connection failure"""
    print_msg("Oh no, there was an error connecting to MAL. Please check your internet connection")


def authorise_user():
    """Get a pair of credentials from the user

    :return: True is successfully authenticated, False if their was an error and user quit
    """
    global credentials

    while True:
        # get the pair of credentials from the user (username, password)
        credentials = auth.get_user_credentials("Please enter your username", "And now your password")

        # check that the credentials are valid
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

    # authenticate the user, return True if successful, else False
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
    # keep prompting for a query until the user quits
    while True:
        click.echo()
        query = click.prompt(credentials[0], prompt_suffix="> ")
        click.echo()

        # process the user query
        processed = process_query(query)

        # quit the program if the user decided
        if processed == qp.Extras.EXIT:
            return


def process_query(query):
    """Process the user query and carry out the requested action

    :param query: A string, the raw user query
    """
    # process the query and get a dictionary with the result
    process_result = qp.process(query)

    # print out the dictionary for debug purposes (REMOVE FOR PRODUCTION!)
    print_msg(str(process_result))

    # the user wants to exit
    if process_result == qp.Extras.EXIT:
        print_msg("Bye bye!")
        return process_result

    # the user said hello
    if process_result["extra"] == qp.Extras.GREETING:
        greetings = ["Hi", "Hello", "Yo"]
        print_msg("{}, {}!".format(random.choice(greetings), credentials[0]))
    # the user said thanks
    elif process_result["extra"] == qp.Extras.THANKS:
        thanks = ["No problem", "You're welcome", "Any time", "You are very welcome"]
        print_msg("{} :D".format(random.choice(thanks)))

    # search database queries
    if process_result["operation"] == qp.OperationType.SEARCH:
        # search for an anime
        if process_result["type"] == qp.MediaType.ANIME:
            search.search(credentials, "anime", process_result["term"])
        # search for a manga
        elif process_result["type"] == qp.MediaType.MANGA:
            search.search(credentials, "manga", process_result["term"])

    # update list entry details queries
    elif process_result["operation"] == qp.OperationType.UPDATE:
        # update anime
        if process_result["type"] == qp.MediaType.ANIME:
            # update anime status
            if process_result["modifier"] == qp.UpdateModifier.STATUS:
                if process_result["value"] == qp.StatusType.WATCHING:
                    update.update_anime_list_entry(credentials, "status", process_result["term"], 1)
                elif process_result["value"] == qp.StatusType.COMPLETED:
                    update.update_anime_list_entry(credentials, "status", process_result["term"], 2)
                elif process_result["value"] == qp.StatusType.ON_HOLD:
                    update.update_anime_list_entry(credentials, "status", process_result["term"], 3)
                elif process_result["value"] == qp.StatusType.DROPPED:
                    update.update_anime_list_entry(credentials, "status", process_result["term"], 4)
                elif process_result["value"] == qp.StatusType.PLAN_TO_WATCH:
                    update.update_anime_list_entry(credentials, "status", process_result["term"], 6)
            # update anime score
            elif process_result["modifier"] == qp.UpdateModifier.SCORE:
                update.update_anime_list_entry(credentials, "score", process_result["term"], process_result["value"])
            # update anime episode count
            elif process_result["modifier"] == qp.UpdateModifier.EPISODE:
                update.update_anime_list_entry(credentials, "episode", process_result["term"], process_result["value"])
        # update manga
        elif process_result["type"] == qp.MediaType.MANGA:
            # update manga status
            if process_result["modifier"] == qp.UpdateModifier.STATUS:
                if process_result["value"] == qp.StatusType.READING:
                    update.update_manga_list_entry(credentials, "status", process_result["term"], 1)
                elif process_result["value"] == qp.StatusType.COMPLETED:
                    update.update_manga_list_entry(credentials, "status", process_result["term"], 2)
                elif process_result["value"] == qp.StatusType.ON_HOLD:
                    update.update_manga_list_entry(credentials, "status", process_result["term"], 3)
                elif process_result["value"] == qp.StatusType.DROPPED:
                    update.update_manga_list_entry(credentials, "status", process_result["term"], 4)
                elif process_result["value"] == qp.StatusType.PLAN_TO_READ:
                    update.update_manga_list_entry(credentials, "status", process_result["term"], 6)
            # update manga score
            elif process_result["modifier"] == qp.UpdateModifier.SCORE:
                update.update_manga_list_entry(credentials, "score", process_result["term"], process_result["value"])
            # update manga chapter count
            elif process_result["modifier"] == qp.UpdateModifier.CHAPTER:
                update.update_manga_list_entry(credentials, "chapter", process_result["term"], process_result["value"])
            # update manga volume count
            elif process_result["modifier"] == qp.UpdateModifier.VOLUME:
                update.update_manga_list_entry(credentials, "volume", process_result["term"], process_result["value"])

    # increment counts for list entries
    elif process_result["operation"] == qp.OperationType.UPDATE_INCREMENT:
        # increment episode count for anime
        if process_result["type"] == qp.MediaType.ANIME:
            update.update_anime_list_entry(credentials, "episode", process_result["term"])
        # increment manga counts
        elif process_result["type"] == qp.MediaType.MANGA:
            # increment chapter count for manga
            if process_result["modifier"] == qp.UpdateModifier.CHAPTER:
                update.update_manga_list_entry(credentials, "chapter", process_result["term"])
            # increment volume count for manga
            elif process_result["modifier"] == qp.UpdateModifier.VOLUME:
                update.update_manga_list_entry(credentials, "volume", process_result["term"])

    # add new entry queries
    elif process_result["operation"] == qp.OperationType.ADD:
        # add new anime entry
        if process_result["type"] == qp.MediaType.ANIME:
            add.add_entry(credentials, "anime", process_result["term"])
        # add new manga entry
        elif process_result["type"] == qp.MediaType.MANGA:
            add.add_entry(credentials, "manga", process_result["term"])

    # delete list entry queries
    elif process_result["operation"] == qp.OperationType.DELETE:
        # delete anime entry
        if process_result["type"] == qp.MediaType.ANIME:
            delete.delete_entry(credentials, "anime", process_result["term"])
        # delete manga entry
        elif process_result["type"] == qp.MediaType.MANGA:
            delete.delete_entry(credentials, "manga", process_result["term"])

    # view all list entries queries
    elif process_result["operation"] == qp.OperationType.VIEW_LIST:
        # view anime list
        if process_result["type"] == qp.MediaType.ANIME:
            update.view_list(credentials[0], "anime")
        # view manga list
        elif process_result["type"] == qp.MediaType.MANGA:
            update.view_list(credentials[0], "manga")

    # default response if the system failed to understand the query
    elif process_result["extra"] is None:
        print_failure()
