import html
from enum import Enum

import click
import requests
from bs4 import BeautifulSoup

import agent
import ui


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


def search(credentials, search_type, search_string, display_details=True):
    """Search for an anime or manga entry and return it

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param search_type: A string denoting the media type to search for, should be either "anime" or "manga"
    :param search_string: A string, the anime or manga to search for
    :param display_details: fsdf
    :return:
    """
    if search_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(search_type, "anime", "manga"))

    url = "https://myanimelist.net/api/{}/search.xml?q={}".format(search_type, search_string.replace(" ", "+"))

    r = ui.threaded_action(requests.get, "Searching", **{"url": url, "auth": credentials, "stream": True})

    if r.status_code == 204:
        agent.print_msg("I'm sorry I could not find any results for \"{}\".".format(search_string))
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
            if display_details:
                display_entry_details(matches[0])
            else:
                return matches[0]
        else:
            agent.print_msg("I found {} results. Did you mean:".format(num_results))

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
                if display_details:
                    display_entry_details(matches[option - 1])
                else:
                    return matches[option - 1]
            else:
                return StatusCode.USER_CANCELLED

