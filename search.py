import click
import requests
from bs4 import BeautifulSoup
import html


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
                # unescape html entities and convert break tags to newlines
                detail_string = html.unescape(detail_string).replace("<br />", "\n")

            click.echo("{}: {}".format(detail_name, detail_string))


def search(credentials, search_type):
    """Search for an anime or manga entry and print out the results

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param search_type: A string denoting the media type to search for, should be either "anime" or "manga"
    :return:
    """
    if search_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(search_type, "anime", "manga"))

    click.echo()

    # get search terms from the user
    search_string = click.prompt("Enter a search term")

    # replace spaces with + chars
    search_query = search_string.replace(" ", "+")

    # prepare the query string
    query_string = "https://myanimelist.net/api/{}/search.xml?q={}".format(search_type, search_query)
    # get the results
    r = requests.get(query_string, auth=credentials, stream=True)

    if r.status_code == 204:
        click.echo("No results found for query \"{}\"".format(search_string))
    else:
        # decode the raw content so beautiful soup can read it as xml not a string
        r.raw.decode_content = True
        soup = BeautifulSoup(r.raw, "xml")

        # get all entries
        all_matched = soup.find_all("entry")
        # store the length of all_matched list since needed multiple times
        num_results = len(all_matched)

        if num_results == 0:
            # shouldn't ever get to here as no results should yield a 204 error, but leave check for now
            click.echo("No results found for query \"{}\"".format(search_string))
        elif num_results == 1:
            display_entry_details(all_matched[0])
        else:
            click.echo("We found {} results. Did you mean:".format(num_results))
            # counter for labelling each element in the list
            i = 1
            for result in all_matched:
                # use a different layout for entries that don't have any synonyms
                title_format = "{}> {} ({})" if result.synonyms.get_text() != "" else "{}> {}"
                click.echo(title_format.format(i, result.title.get_text(), result.synonyms.get_text()))
                i += 1

            click.echo("{}> [None of these]".format(num_results + 1))

            # get a valid choice from the user
            while True:
                option = click.prompt("Please choose an option", type=int)
                if 1 <= option <= num_results + 1:
                    break
                else:
                    click.echo("You must enter a value between {} and {}".format(1, num_results + 1))

            # check that the user didn't choose the none of these option before trying to display entry
            if option != num_results + 1:
                display_entry_details(all_matched[option - 1])

    # await a keypress before continuing so that it doesn't go straight back to menu
    click.pause()


def anime_search(credentials):
    """Search for an anime and print out the results

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    search(credentials, "anime")


def manga_search(credentials):
    """Search for a manga and print out the results

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    search(credentials, "manga")
