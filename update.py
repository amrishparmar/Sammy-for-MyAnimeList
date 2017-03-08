import click
import requests
from bs4 import BeautifulSoup
from constants import ANIME_STATUS_MAP, ANIME_TYPE_MAP, MANGA_STATUS_MAP, MANGA_TYPE_MAP
import helpers


def _update_anime_list_entry(credentials, field_type, anime_entry, new_value=None):
    """Update the details of a users anime list entry

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param field_type: A string, the detail to update, must be either "episode", "status" or "score"
    :param anime_entry: A beautiful soup tag, the entry on the list to update
    :param new_value: An int (or string) or None, the new value to set for the field_type
    """

    # the valid types of fields to update
    valid_field_types = ["episode", "status", "score"]

    # ensure that the field_type is valid
    if field_type not in valid_field_types:
        raise ValueError("Invalid argument for {}, must be one of {}.".format(field_type, valid_field_types))

    # check that the anime_entry is valid
    if anime_entry is not None:
        xml_tag_format = "<{0}>{1}</{0}>"
        xml_field_tags = ""

        new_status = 0

        # if we are incrementing the episode count for an anime
        if field_type == "episode":
            # we are are incrementing the count
            if new_value is None:
                current_ep_count = int(anime_entry.my_watched_episodes.get_text())
                new_value = current_ep_count + 1

            # check if the user has reached the last episode
            if new_value == int(anime_entry.series_episodes.get_text()):
                click.echo("Episode {} is the last in the series.".format(new_value))
                if click.confirm("Do you wish to change the status to completed?"):
                    xml_field_tags += xml_tag_format.format("status", "2")
                    new_status = 2
            # check if the user has a status of not watching
            elif anime_entry.my_status.get_text() != "1":
                if click.confirm("Do you wish to change the status to watching?"):
                    xml_field_tags += xml_tag_format.format("status", "1")
                    new_status = 1

        xml_field_tags += xml_tag_format.format(field_type, new_value)

        # prepare xml data and url for sending to server
        xml = '<?xml version="1.0" encoding="UTF-8"?><entry>{}</entry>'.format(xml_field_tags)
        url = "https://myanimelist.net/api/animelist/update/{}.xml".format(anime_entry.series_animedb_id.get_text())

        # send the request to the server, uses GET due to bug in API handling POST requests
        r = requests.get(url, params={"data": xml}, auth=credentials)

        # inform the user whether the request was successful or not
        if r.status_code == 200:
            updated_msg_format = 'Updated "{}" to {} "{}".'

            anime_title = anime_entry.series_title.get_text()

            updated_msg = updated_msg_format.format(anime_title, field_type, new_value)

            if field_type == "status":
                updated_msg = updated_msg_format.format(anime_title, field_type, ANIME_STATUS_MAP[str(new_value)])
            # check if the status was changed
            elif new_status:
                updated_msg += " Status set to \"{}\"".format(ANIME_STATUS_MAP[str(new_status)])

            click.echo(updated_msg)
        else:
            click.echo("Error updating anime. Please try again.")

    click.pause()


def increment_episode_count(credentials):
    """Search for and increment the episode count by 1 for an anime on user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "anime")

    if result is not None:
        _update_anime_list_entry(credentials, "episode", result)


def set_episode_count(credentials):
    """Search for and set the episode count for an anime on user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "anime")

    # check that the search returned a valid result
    if result is not None:
        episodes = helpers.get_new_count_from_user("episode")
        _update_anime_list_entry(credentials, "episode", result, episodes)


def set_anime_score(credentials):
    """Search for and set the score for an anime on user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :return: None, when the score is updated
    """
    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "anime")

    # check that the search returned a valid result
    if result is not None:
        score = helpers.get_score_choice_from_user()
        if score is not None:
            _update_anime_list_entry(credentials, "score", result, score)


def set_anime_status(credentials):
    """Search for and set the status for an anime on user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "anime")

    # check that the search returned a valid result
    if result is not None:
        status = helpers.get_status_choice_from_user("anime")

        _update_anime_list_entry(credentials, "status", result, status)


def _update_manga_list_entry(credentials, field_type, manga_entry, new_value=None):
    """Increment the chapter or volume count of a manga on the user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param field_type: A string, the detail to update, must be either "chapter", "volume", "status" or "score"
    :param manga_entry: A beautiful soup tag, the entry on the list to update
    :param new_value: An int (or string) or None, the new value to set for the field_type
    """

    valid_field_types = ["chapter", "volume", "status", "score"]

    # ensure that the field_type is valid
    if field_type not in valid_field_types:
        raise ValueError("Invalid argument for {}, must be one of {}.".format(field_type, valid_field_types))

    # check the searching the list returned a valid result
    if manga_entry is not None:
        manga_title = manga_entry.series_title.get_text()

        xml_tag_format = "<{0}>{1}</{0}>"
        xml_field_tags = ""

        new_status = 0

        # if we are changing the chapter or volume count for a manga
        if field_type in ["chapter", "volume"]:
            # we are incrementing the count
            if new_value is None:
                if field_type == "chapter":
                    current_value = int(manga_entry.my_read_chapters.get_text())
                else:
                    current_value = int(manga_entry.my_read_volumes.get_text())
                new_value = current_value + 1

            series_chapters = int(manga_entry.series_chapters.get_text())
            series_volumes = int(manga_entry.series_volumes.get_text())

            # check if the user has reached either the last chapter or last volume
            if (new_value == series_chapters and field_type == "chapter") or \
               (new_value == series_volumes and field_type == "volume"):
                click.echo("{} {} is the last in the series.".format(field_type.title(), new_value))
                if click.confirm("Do you wish to change the status to completed?"):
                    # set both the chapter and volume counts to the number in the series
                    xml_field_tags += xml_tag_format.format("status", "2")
                    xml_field_tags += xml_tag_format.format("chapter", series_chapters)
                    xml_field_tags += xml_tag_format.format("volume", series_volumes)
                    new_status = 2
            # check if the user has a status of not reading
            elif manga_entry.my_status.get_text() != "1":
                if click.confirm("Do you wish to change the status to watching?"):
                    xml_field_tags += xml_tag_format.format("status", "1")
                    new_status = 1

        if new_status != 2:
            xml_field_tags += xml_tag_format.format(field_type, new_value)

        # prepare xml data and url for sending to server
        xml = '<?xml version="1.0" encoding="UTF-8"?><entry>{}</entry>'.format(xml_field_tags)
        url = "https://myanimelist.net/api/mangalist/update/{}.xml".format(manga_entry.series_mangadb_id.get_text())

        # send the request to the server, uses GET due to bug in API handling POST requests
        r = requests.get(url, params={"data": xml}, auth=credentials)

        # inform the user whether the request was successful or not
        if r.status_code == 200:
            updated_msg_format = "Updated \"{}\" to {} {}."

            updated_msg = updated_msg_format.format(manga_title, field_type, new_value)

            if field_type == "status":
                updated_msg = updated_msg_format.format(manga_title, field_type, MANGA_STATUS_MAP[str(new_value)])
            # check if the status was changed
            elif new_status:
                updated_msg += " Status set to \"{}\"".format(MANGA_STATUS_MAP[str(new_status)])

            click.echo(updated_msg)
        else:
            click.echo("Error updating manga. Please try again.")

    click.pause()


def increment_chapter_count(credentials):
    """Search for and increment the chapter count by 1 for a manga on user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """

    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "manga")

    if result is not None:
        _update_manga_list_entry(credentials, "chapter", result)


def increment_volume_count(credentials):
    """Search for and increment the volume count by 1 for a manga on user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """

    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "manga")

    if result is not None:
        _update_manga_list_entry(credentials, "volume", result)


def set_chapter_count(credentials):
    """Search for and set the chapter count for a manga on user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "manga")

    # check that the search returned a valid result
    if result is not None:
        chapters = helpers.get_new_count_from_user("chapter")
        _update_manga_list_entry(credentials, "chapter", result, chapters)


def set_volume_count(credentials):
    """Search for and set the volume count for a manga on user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    # prompt the user to search their list for the entry
    result = search_list(credentials[0], "manga")

    # check that the search returned a valid result
    if result is not None:
        volumes = helpers.get_new_count_from_user("volume")
        _update_manga_list_entry(credentials, "volume", result, volumes)


def set_manga_score(credentials):
    """Search for and set the score for a manga on user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :return: None when the score is updated
    """
    result = search_list(credentials[0], "manga")

    # check that the search returned a valid result
    if result is not None:
        score = helpers.get_score_choice_from_user()
        if score is not None:
            _update_manga_list_entry(credentials, "score", result, score)


def set_manga_status(credentials):
    """Search for and set the status for a manga on user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """

    result = search_list(credentials[0], "manga")

    # check that the search returned a valid result
    if result is not None:
        status = helpers.get_status_choice_from_user("manga")

        _update_manga_list_entry(credentials, "status", result, status)


def search_list(username, search_type):
    """Search a user's list for a manga or anime and return the matching entry

    :param username: A string, the username of a MAL user
    :param search_type: A string, must be either "anime" or "manga"
    :return: A beautiful soup tag or None if unsuccessful
    """

    if search_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(search_type, "anime", "manga"))

    click.echo()

    while True:
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
            if click.confirm("Try again?"):
                continue
            else:
                return
        elif num_results == 1:
            return matches[0]
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
                return matches[option - 1]


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
