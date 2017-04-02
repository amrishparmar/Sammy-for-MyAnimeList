import html
from enum import Enum

import click
import requests
from bs4 import BeautifulSoup

import agent
# from . import add


class StatusCode(Enum):
    NO_RESULTS = 0
    USER_CANCELLED = 1


def display_entry_details(entry):
    """Display all the details of a given entry

    :param entry: an anime or manga entry as a Beautiful Soup Tag object
    """
    for detail in entry.children:
        # ignore newlines in children
        if detail != "\n":
            # replace in tag name the underscores with spaces and convert to title case
            detail_name = detail.name.replace("_", " ").title()

            # set the string to be the detail.string by default
            detail_string = detail.string

            # check that the string contains something
            if detail_string is not None:
                # unescape html entities and remove break tags
                detail_string = html.unescape(detail_string).replace("<br />", "")

            click.echo("{}: {}".format(detail_name, detail_string))


def search(credentials, search_type, search_string):
    """Search for an anime or manga entry and return it

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param search_type: A string denoting the media type to search for, should be either "anime" or "manga"
    :param search_string: A string, the anime or manga to search for
    :return:
    """
    if search_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(search_type, "anime", "manga"))

    # get the results
    r = requests.get("https://myanimelist.net/api/{}/search.xml?q={}".format(
        search_type, search_string.replace(" ", "+")), auth=credentials, stream=True)

    if r.status_code == 204:
        return StatusCode.NO_RESULTS
    else:
        # decode the raw content so beautiful soup can read it as xml not a string
        r.raw.decode_content = True
        soup = BeautifulSoup(r.raw, "xml")

        # get all entries
        matches = soup.find_all("entry")

        # store the length of all_matched list since needed multiple times
        num_results = len(matches)

        if num_results == 1:
            return matches[0]
        else:
            agent.print_msg("We found {} results. Did you mean:".format(num_results))

            # iterate over the matches and print them out
            for i in range(num_results):
                # use a different layout for entries that don't have any synonyms
                title_format = "{}> {} ({})" if matches[i].synonyms.get_text() != "" else "{}> {}"
                click.echo(title_format.format(i + 1, matches[i].title.get_text(), matches[i].synonyms.get_text()))

            click.echo("{}> [None of these]".format(num_results + 1))

            # get a valid choice from the user
            while True:
                option = click.prompt("Please choose an option", type=int)
                if 1 <= option <= num_results + 1:
                    break
                else:
                    click.echo("You must enter a value between {} and {}".format(1, num_results + 1))

            click.echo()

            # check that the user didn't choose the none of these option before trying to display entry
            if option != num_results + 1:
                return matches[option - 1]
            else:
                return StatusCode.USER_CANCELLED


def anime_search(credentials, search_string):
    """Search for an anime and print out the results

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param search_string: fsdf
    :return:
    """

    result = search(credentials, "anime", search_string)

    if result != StatusCode.USER_CANCELLED and result != StatusCode.NO_RESULTS:
        agent.print_msg("Here is the entry you wanted.\r\n")
        display_entry_details(result)

        # if click.confirm("Add this entry to your anime list?"):
        #     add.add_anime_entry(credentials, entry=result)
    elif result == StatusCode.NO_RESULTS:
        agent.print_msg("I'm sorry I could not find any results for \"{}\".".format(search_string))


def manga_search(credentials, search_string):
    """Search for a manga and print out the results

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param search_string: fsdf
    :return:
    """

    result = search(credentials, "manga", search_string)

    if result != StatusCode.USER_CANCELLED and result != StatusCode.NO_RESULTS:
        agent.print_msg("Here is the entry you wanted.")
        display_entry_details(result)

        # if click.confirm("Add this entry to your manga list?"):
        #     add.add_manga_entry(credentials, entry=result)
    elif result == StatusCode.NO_RESULTS:
        agent.print_msg("I'm sorry I could not find any results for \"{}\".".format(search_string))
