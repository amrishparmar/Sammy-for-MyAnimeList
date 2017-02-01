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
            # unescape html entities and convert break tags to newlines
            detail_string = html.unescape(detail.string).replace("<br />", "\n")

            click.echo("{}: {}".format(detail_name, detail_string))


def anime_search(credentials):
    """Search for an anime and print out the results

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    click.echo()
    search = click.prompt("Enter a search term")
    search_query = "+".join(search.split())
    query_string = "https://myanimelist.net/api/anime/search.xml?q={}".format(search_query)
    r = requests.get(query_string, auth=credentials, stream=True)
    r.raw.decode_content = True
    soup = BeautifulSoup(r.raw, "xml")

    all_matched = soup.find_all("entry")
    num_results = len(all_matched)

    if num_results == 0:
        click.echo("No results found for query \"{}\"".format(search))
    elif num_results == 1:
        display_entry_details(all_matched[0])
    else:
        click.echo("We found {} results. Did you mean:".format(num_results))
        i = 1
        for result in all_matched:
            title_format = "{}> {} ({})" if result.synonyms.get_text() != "" else "{}> {}"
            click.echo(title_format.format(i, result.title.get_text(), result.synonyms.get_text()))
            i += 1

        while True:
            option = click.prompt("Please choose an option", type=int)
            if 1 <= option <= num_results:
                break
            else:
                click.echo("You must enter a value between {} and {}".format(1, num_results))

        display_entry_details(all_matched[option - 1])

    click.pause()




def manga_search(credentials):
    pass
