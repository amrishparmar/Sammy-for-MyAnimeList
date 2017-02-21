import click
import requests
from bs4 import BeautifulSoup
from constants import ANIME_STATUS_MAP, ANIME_TYPE_MAP, MANGA_STATUS_MAP, MANGA_TYPE_MAP


def _update_anime_list_entry(credentials, field_type, result_list, new_value=None):
    """Increment the episode count of an anime on the user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """

    valid_field_types = ["episode", "status", "score"]

    # ensure that the field_type is valid
    if field_type not in valid_field_types:
        raise ValueError("Invalid argument for {}, must be one of {}.".format(field_type, valid_field_types))

    # check the searching the list returned a valid result
    if result_list is not None:
        # store the data contained in result
        anime_entry, list_data_xml = result_list

        # get the id of the anime to update
        anime_id = anime_entry.series_animedb_id.get_text()

        anime_title = ""

        # iterate over all anime entries
        for entry in list_data_xml.find_all("anime"):
            # check if the current entry is the one we are looking for
            if entry.series_animedb_id.get_text() == anime_id:
                if field_type == "episode" and new_value is None:
                    # get the current number of episodes watched for the anime and the title
                    current_ep_count = int(entry.my_watched_episodes.get_text())
                    new_value = current_ep_count + 1

                anime_title = entry.series_title.get_text()
                break

        # prepare xml data for sending to server
        xml = """<?xml version="1.0" encoding="UTF-8"?><entry><{0}>{1}</{0}></entry>""".format(field_type, new_value)

        # send the request to the server, uses GET due to bug in API handling POST requests
        r = requests.get("https://myanimelist.net/api/animelist/update/{}.xml?data={}".format(anime_id, xml),
                         auth=credentials)

        # inform the user whether the request was successful or not
        if r.status_code == 200:
            click.echo("Updated \"{}\" to {} {}".format(anime_title, field_type, new_value))
        else:
            click.echo("Error updating anime. Please try again.")

    click.pause()


def increment_episode_count(credentials):
    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "anime")

    _update_anime_list_entry(credentials, "episode", result)


def set_episode_count(credentials):
    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "anime")

    if result is not None:
        episodes = click.prompt("Enter the new episode count", type=int)
        _update_anime_list_entry(credentials, "episode", result, episodes)
    else:
        click.pause()


def set_anime_score(credentials):
    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "anime")

    if result is not None:
        while True:
            score = click.prompt("Enter the new score", type=int)

            if 0 < score < 11:
                break
            else:
                click.echo("You must enter a value between 1 and 10.")

        _update_anime_list_entry(credentials, "score", result, score)
    else:
        click.pause()


def set_anime_status(credentials):
    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "anime")

    if result is not None:
        click.echo("Which of the following statuses do you want to update to?")

        for i in range(1, len(ANIME_STATUS_MAP.keys()) + 1):
            click.echo("{}> {}".format(i, ANIME_STATUS_MAP[str(i) if i != 5 else str(6)]))

        while True:
            status = click.prompt("Choose an option", type=int)

            last_option = int(list(ANIME_STATUS_MAP.keys())[-1])

            if 0 < status < last_option:
                break
            else:
                click.echo("You must enter a value between 1 and {}.".format(last_option))

        _update_anime_list_entry(credentials, "status", result, status)
    else:
        click.pause()


def _update_manga_list_entry(credentials, field_type, result_list, new_value=None):
    """Increment the chapter or volume count of a manga on the user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param field_type: A string, must be either "chapter" or "volume"
    """

    valid_field_types = ["chapter", "volume", "status", "score"]

    # ensure that the field_type is valid
    if field_type not in valid_field_types:
        raise ValueError("Invalid argument for {}, must be one of {}.".format(field_type, valid_field_types))

    # check the searching the list returned a valid result
    if result_list is not None:
        # store the data contained in result
        manga_entry, list_data_xml = result_list

        # get the id of the manga to update
        manga_id = manga_entry.series_mangadb_id.get_text()

        manga_title = ""

        # iterate over all manga entries
        for entry in list_data_xml.find_all("manga"):
            # check if the current entry is the one we are looking for
            if entry.series_mangadb_id.get_text() == manga_id:
                # if we are incrementing, not just setting
                if new_value is None and field_type in ["chapter", "volume"]:
                    if field_type == "chapter":
                        current_value = int(entry.my_read_chapters.get_text())
                    else:
                        current_value = int(entry.my_read_volumes.get_text())
                    new_value = current_value + 1

                manga_title = entry.series_title.get_text()
                break

        # prepare xml data for sending to server
        xml = '<?xml version="1.0" encoding="UTF-8"?><entry><{0}>{1}</{0}></entry>'.format(field_type, new_value)

        # send the request to the server, uses GET due to bug in API handling POST requests
        r = requests.get("https://myanimelist.net/api/mangalist/update/{}.xml?data={}".format(manga_id, xml),
                         auth=credentials)

        # inform the user whether the request was successful or not
        if r.status_code == 200:
            click.echo("Updated \"{}\" to {} {}".format(manga_title, field_type, new_value))
        else:
            click.echo("Error updating manga. Please try again.")

    click.pause()


def increment_chapter_count(credentials):
    """Increment the chapter count of a manga on the user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """

    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "manga")
    _update_manga_list_entry(credentials, "chapter", result)


def increment_volume_count(credentials):
    """Increment the volume count of a manga on the user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "manga")
    _update_manga_list_entry(credentials, "volume", result)


def set_chapter_count(credentials):
    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "manga")

    if result is not None:
        chapters = click.prompt("Enter the new chapter count", type=int)
        _update_manga_list_entry(credentials, "chapter", result, chapters)
    else:
        click.pause()


def set_volume_count(credentials):
    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "manga")

    if result is not None:
        volumes = click.prompt("Enter the new volume count", type=int)
        _update_manga_list_entry(credentials, "volume", result, volumes)
    else:
        click.pause()


def set_manga_score(credentials):
    result = search_list(credentials[0], "manga")

    if result is not None:
        while True:
            score = click.prompt("Enter the new score", type=int)

            if 0 < score < 11:
                break
            else:
                click.echo("You must enter a value between 1 and 10.")

        _update_manga_list_entry(credentials, "score", result, score)
    else:
        click.pause()


def set_manga_status(credentials):
    result = search_list(credentials[0], "manga")

    if result is not None:
        click.echo("Which of the following statuses do you want to update to?")

        for i in range(1, len(MANGA_STATUS_MAP.keys()) + 1):
            click.echo("{}> {}".format(i, MANGA_STATUS_MAP[str(i) if i != 5 else str(6)]))

        while True:
            status = click.prompt("Choose an option", type=int)

            last_option = int(list(MANGA_STATUS_MAP.keys())[-1])

            if 0 < status < last_option:
                break
            else:
                click.echo("You must enter a value between 1 and {}.".format(last_option))

        _update_manga_list_entry(credentials, "status", result, status)
    else:
        click.pause()


def search_list(username, search_type):
    """Search a user's list for a manga or anime and return the list of matching entries

    :param username: A string, the username of a MAL user
    :param search_type: A string, must be either "anime" or "manga"
    :return:
    """

    if search_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(search_type, "anime", "manga"))

    click.echo()

    # get an anime or manga title from the user
    search_string = click.prompt("Enter name of {} to update".format(search_type))

    # normalise to lowercase for easier searching
    search_lower = search_string.lower()

    # store the search string as a list of tokens
    search_tokens = search_lower.split()

    # make the request to the server and get the results
    r = requests.get("https://myanimelist.net/malappinfo.php", params={"u": username, "type": search_type}, stream=True)
    r.raw.decode_content = True

    soup = BeautifulSoup(r.raw, "xml")

    matches = []

    # iterate over the returned entries for the search type
    for entry in soup.find_all(search_type):
        # normalise the title and synonyms to lowercase
        series_title_lower = entry.series_title.get_text().lower()
        series_synonyms_lower = entry.series_synonyms.get_text().lower()

        # if the whole search string matches the entry then add it to our list of matches
        if search_lower in series_title_lower or search_lower in series_synonyms_lower:
            matches.append(entry)
            continue

        # check if any of our tokens matches the entry
        for token in search_tokens:
            if token in series_title_lower or token in series_synonyms_lower:
                matches.append(entry)
                break

    num_results = len(matches)

    if num_results == 0:
        click.echo("Could not find {} matching \"{}\" on your list".format(search_type, search_string))
        return
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


def view_list(username, search_type):
    """View the anime and manga list of a user

    :param username: A valid MAL username
    :param search_type: A string, must be either "anime" or "manga"
    """
    if search_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(search_type, "anime", "manga"))

    # the base url of the user list xml data
    malappinfo = "https://myanimelist.net/malappinfo.php"

    # make the request to the server and get the results
    r = requests.get(malappinfo, params={"u": username, "type": search_type}, stream=True)
    r.raw.decode_content = True

    soup = BeautifulSoup(r.raw, "xml")

    i = 1
    for entry in soup.find_all(search_type):
        # use a different layout depending on whether it is anime or manga
        layout_string = "{}> {}" + ("\n    - {}: {}" * (4 if search_type == "anime" else 5))

        if search_type == "anime":
            click.echo(layout_string.format(
                i, entry.series_title.get_text(),
                "Status", ANIME_STATUS_MAP[entry.my_status.get_text()],
                "Score", entry.my_score.get_text(),
                "Type", ANIME_TYPE_MAP[entry.series_type.get_text()],
                "Progress", entry.my_watched_episodes.get_text() + "/" + entry.series_episodes.get_text()))
        else:
            click.echo(layout_string.format(
                i, entry.series_title.get_text(),
                "Status", MANGA_STATUS_MAP[entry.my_status.get_text()],
                "Score", entry.my_score.get_text(),
                "Type", MANGA_TYPE_MAP[entry.series_type.get_text()],
                "Chapters", entry.my_read_chapters.get_text() + "/" + entry.series_chapters.get_text(),
                "Volumes", entry.my_read_volumes.get_text() + "/" + entry.series_volumes.get_text()))

        i += 1

    click.pause()


def view_anime_list(credentials):
    """View the anime list of a user

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    view_list(credentials[0], "anime")


def view_manga_list(credentials):
    """View the manga list of a user

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    view_list(credentials[0], "manga")
