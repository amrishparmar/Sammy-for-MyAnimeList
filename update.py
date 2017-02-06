import click
import requests
from bs4 import BeautifulSoup


def increment_episode_count(credentials):
    """Increment the episode count of an anime on the user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """

    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "anime")

    # check the searching the list returned a valid result
    if result is not None:
        # store the data contained in result
        anime_entry, list_data_xml = result

        # get the id of the anime to update
        anime_id = anime_entry.series_animedb_id.get_text()

        current_ep_count = 0
        anime_title = ""

        # iterate over all anime entries
        for entry in list_data_xml.find_all("anime"):
            # check if the current entry is the one we are looking for
            if entry.series_animedb_id.get_text() == anime_id:
                # get the current number of episodes watched for the anime and the title
                current_ep_count = int(entry.my_watched_episodes.get_text())
                anime_title = entry.series_title.get_text()

        # prepare xml data for sending to server
        xml = """<?xml version="1.0" encoding="UTF-8"?><entry><episode>{}</episode></entry>""".format(
            current_ep_count + 1)

        # send the request to the server, uses GET due to bug in API handling POST requests
        r = requests.get("https://myanimelist.net/api/animelist/update/{}.xml?data={}".format(anime_id, xml),
                         auth=credentials)

        # inform the user whether the request was successful or not
        if r.status_code == 200:
            click.echo("Updated \"{}\" to episode {}".format(anime_title, current_ep_count + 1))
        else:
            click.echo("Error updating anime. Please try again.")

    click.pause()


def increment_chapter_volume_count(credentials, field_type):
    """Increment the chapter or volume count of a manga on the user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param field_type: A string, must be either "chapter" or "volume"
    """

    # ensure that the field_type is valid
    if field_type not in ["chapter", "volume"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(field_type, "chapter", "volume"))

    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "manga")

    # check the searching the list returned a valid result
    if result is not None:
        # store the data contained in result
        manga_entry, list_data_xml = result

        # get the id of the manga to update
        manga_id = manga_entry.series_mangadb_id.get_text()

        current_field_count = 0
        manga_title = ""

        # iterate over all manga entries
        for entry in list_data_xml.find_all("manga"):
            # check if the current entry is the one we are looking for
            if entry.series_mangadb_id.get_text() == manga_id:
                # get the current number of chapters or volumes for the manga and the title
                current_field_count = int(
                    entry.my_read_chapters.get_text() if field_type == "chapter" else entry.my_read_volumes.get_text())
                manga_title = entry.series_title.get_text()

        # prepare xml data for sending to server
        xml = """<?xml version="1.0" encoding="UTF-8"?><entry><{0}>{1}</{0}></entry>""".format(field_type,
                                                                                               current_field_count + 1)

        # send the request to the server, uses GET due to bug in API handling POST requests
        r = requests.get("https://myanimelist.net/api/mangalist/update/{}.xml?data={}".format(manga_id, xml),
                         auth=credentials)

        # inform the user whether the request was successful or not
        if r.status_code == 200:
            click.echo("Updated \"{}\" to chapter {}".format(manga_title, current_field_count + 1))
        else:
            click.echo("Error updating manga. Please try again.")

    click.pause()


def increment_chapter_count(credentials):
    """Increment the chapter count of a manga on the user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    increment_chapter_volume_count(credentials, "chapter")


def increment_volume_count(credentials):
    """Increment the volume count of a manga on the user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    increment_chapter_volume_count(credentials, "volume")


def search_list(username, search_type):
    """Search a user's list for a manga or anime and return the list of matching entries

    :param username: A string, the username of a MAL user
    :param search_type: A string, which
    :return:
    """
    if search_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(search_type, "anime", "manga"))

    click.echo()

    # get an anime or manga title from the user
    search_string = click.prompt("Enter name of {} to update".format(search_type))

    # normalise to lowercase for easier searching
    search_string = search_string.lower()

    # store the search string as a list of tokens
    search_tokens = search_string.split()

    # the base url of the user list xml data
    malappinfo = "https://myanimelist.net/malappinfo.php"

    # make the request to the server and get the results
    r = requests.get(malappinfo, params={"u": username, "type": search_type}, stream=True)
    r.raw.decode_content = True

    soup = BeautifulSoup(r.raw, "xml")

    matches = []

    # iterate over the returned entries for the search type
    for entry in soup.find_all(search_type):
        # normalise the title and synonyms to lowercase
        series_title_lower = entry.series_title.get_text().lower()
        series_synonyms_lower = entry.series_synonyms.get_text().lower()

        # if the whole search string matches the entry then add it to our list of matches
        if search_string in series_title_lower or search_string in series_synonyms_lower:
            matches.append(entry)
            continue

        # check if any of our tokens matches the entry
        for token in search_tokens:
            if token in series_title_lower or token in series_synonyms_lower:
                matches.append(entry)
                break

    num_results = len(matches)

    if num_results == 0:
        click.echo("No results found")
        return None
    elif num_results == 1:
        return matches[0], soup
    else:
        click.echo("We found {} results. Did you mean:".format(num_results))

        # iterate over the matches and print them out
        for i in range(len(matches)):
            title_format = "{}> {} ({})" if matches[i].series_synonyms.get_text() != "" else "{}> {}"
            click.echo(title_format.format(i + 1, matches[i].series_title.get_text(),
                                           matches[i].series_synonyms.get_text()))

        click.echo("{}> [None of these]".format(num_results + 1))

        # get a valid choice from the user
        while True:
            option = click.prompt("Please choose an option", type=int)
            if 1 <= option <= num_results + 1:
                break
            else:
                click.echo("You must enter a value between {} and {}".format(1, num_results + 1))

        # check that the user didn't choose the none of these option before returning the match
        if option != num_results + 1:
            return matches[option - 1], soup
