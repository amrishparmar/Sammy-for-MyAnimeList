from enum import Enum

import click
import requests
from bs4 import BeautifulSoup

import agent
from constants import ANIME_STATUS_MAP, ANIME_TYPE_MAP, MANGA_STATUS_MAP, MANGA_TYPE_MAP
import network
import ui


class ListSearchStatusCode(Enum):
    """"An Enum represented the type of result of list searches"""
    NO_RESULTS = 0
    USER_CANCELLED = 1


def update_anime_list_entry(credentials, field_type, search_string, new_value=None):
    """Update the details of a users anime list entry

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param field_type: A string, the detail to update, must be either "episode", "status" or "score"
    :param search_string: A string, the anime that the user wants to update
    :param new_value: An int or None, the new value to set for the field_type
    """

    # the valid types of fields to update
    valid_field_types = ["episode", "status", "score"]

    # ensure that the field_type is valid
    if field_type not in valid_field_types:
        raise ValueError("Invalid argument for {}, must be one of {}.".format(field_type, valid_field_types))

    # get the BeautifulSoup tag corresponding to the user's search phrase
    anime_entry = search_list(credentials[0], "anime", search_string)

    # check that a valid match was returned
    if anime_entry == ListSearchStatusCode.USER_CANCELLED:
        agent.print_msg("I have cancelled the operation. Nothing was changed.")
        return

    elif anime_entry == network.StatusCode.CONNECTION_ERROR or anime_entry == network.StatusCode.OTHER_ERROR \
            or anime_entry == ListSearchStatusCode.NO_RESULTS:
        return
    else:
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
                agent.print_msg("Episode {} is the last in the series.".format(new_value))
                if click.confirm("Sammy> Do you wish to change the status to completed?"):
                    xml_field_tags += xml_tag_format.format("status", "2")
                    new_status = 2
            # check if the user has a status of not watching
            elif anime_entry.my_status.get_text() != "1":
                if click.confirm("Sammy> Do you wish to change the status to watching?"):
                    xml_field_tags += xml_tag_format.format("status", "1")
                    new_status = 1

        # set the number of episodes to number in series if status set to completed
        elif field_type == "status" and new_value == 2 and anime_entry.series_episodes.get_text() != "0":
            xml_field_tags += xml_tag_format.format("episode", anime_entry.series_episodes.get_text())

        xml_field_tags += xml_tag_format.format(field_type, new_value)

        # prepare xml data and url for sending to server
        xml = '<?xml version="1.0" encoding="UTF-8"?><entry>{}</entry>'.format(xml_field_tags)
        url = "https://myanimelist.net/api/animelist/update/{}.xml".format(anime_entry.series_animedb_id.get_text())

        # send the async request to the server, uses GET due to bug in API handling POST requests
        r = ui.threaded_action(network.make_request, msg="Updating", request=requests.get, url=url,
                               params={"data": xml}, auth=credentials)

        # check if there was an error with the user's internet connection
        if r == network.StatusCode.CONNECTION_ERROR:
            agent.print_connection_error_msg()
            return

        # inform the user whether the request was successful or not
        if r.status_code == 200:
            anime_title = anime_entry.series_title.get_text()
            updated_msg_format = 'I have updated "{}" to {} "{}".'
            updated_msg = updated_msg_format.format(anime_title, field_type, new_value)

            if field_type == "status":
                updated_msg = updated_msg_format.format(anime_title, field_type, ANIME_STATUS_MAP[str(new_value)])
            # check if the status was changed
            elif new_status:
                updated_msg += " Status set to \"{}\"".format(ANIME_STATUS_MAP[str(new_status)])

            agent.print_msg(updated_msg)
        else:
            agent.print_msg("There was an error updating the anime. Please try again.")


def update_manga_list_entry(credentials, field_type, search_string, new_value=None):
    """Increment the chapter or volume count of a manga on the user's list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param field_type: A string, the detail to update, must be either "chapter", "volume", "status" or "score"
    :param search_string: A string, the manga that the user wants to update
    :param new_value: An int or None, the new value to set for the field_type
    """

    valid_field_types = ["chapter", "volume", "status", "score"]

    # ensure that the field_type is valid
    if field_type not in valid_field_types:
        raise ValueError("Invalid argument for {}, must be one of {}.".format(field_type, valid_field_types))

    if field_type == "score" and 1 > new_value > 10:
        agent.print_msg("I'm sorry, but the new score value must be between 1 and 10.")
        return

    if new_value is not None and new_value < 0:
        agent.print_msg("The value for {} cannot be less than 0.".format(field_type))
        return

    # get the BeautifulSoup tag corresponding to the user's search phrase
    manga_entry = search_list(credentials[0], "manga", search_string)

    # check that a valid match was returned
    if manga_entry == ListSearchStatusCode.USER_CANCELLED:
        agent.print_msg("I have cancelled the operation. Nothing was changed.")
        return
    elif manga_entry == network.StatusCode.CONNECTION_ERROR or manga_entry == network.StatusCode.OTHER_ERROR \
            or manga_entry == ListSearchStatusCode.NO_RESULTS:
        return
    else:
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

            if field_type == "chapters" and series_chapters != 0 and new_value > series_chapters:
                agent.print_msg("There are only {} chapters in this series.".format(series_chapters))
                return
            elif field_type == "volumes" and series_volumes != 0 and new_value > series_volumes:
                agent.print_msg("There are only {} volumes in this series.".format(series_volumes))
                return

            # check if the user has reached either the last chapter or last volume
            if (new_value == series_chapters and field_type == "chapter" and series_chapters != 0) or \
               (new_value == series_volumes and field_type == "volume" and series_volumes != 0):
                agent.print_msg("{} {} is the last in the series.".format(field_type.title(), new_value))
                if click.confirm("Sammy> Do you wish to change the status to completed?"):
                    # set both the chapter and volume counts to the number in the series
                    xml_field_tags += xml_tag_format.format("status", "2")
                    xml_field_tags += xml_tag_format.format("chapter", series_chapters)
                    xml_field_tags += xml_tag_format.format("volume", series_volumes)
                    new_status = 2
            # check if the user has a status of not reading
            elif manga_entry.my_status.get_text() != "1":
                if click.confirm("Sammy> Do you wish to change the status to watching?"):
                    xml_field_tags += xml_tag_format.format("status", "1")
                    new_status = 1

        # set the number of chapters and volumes to number in series if status set to completed
        elif field_type == "status" and new_value == 2:
            if manga_entry.series_chapters.get_text() != "0":
                xml_field_tags += xml_tag_format.format("chapter", manga_entry.series_chapters.get_text())
            if manga_entry.series_volumes.get_text() != "0":
                xml_field_tags += xml_tag_format.format("volume", manga_entry.series_volumes.get_text())

        if new_status != 2:
            xml_field_tags += xml_tag_format.format(field_type, new_value)

        # form the xml string
        xml = '<?xml version="1.0" encoding="UTF-8"?><entry>{}</entry>'.format(xml_field_tags)

        # prepare the url
        url = "https://myanimelist.net/api/mangalist/update/{}.xml".format(manga_entry.series_mangadb_id.get_text())

        # send the async request to the server, uses GET due to bug in API handling POST requests
        r = ui.threaded_action(network.make_request, msg="Updating", request=requests.get, url=url,
                               params={"data": xml}, auth=credentials)

        if r == network.StatusCode.CONNECTION_ERROR:
            agent.print_connection_error_msg()
            return

        # inform the user whether the request was successful or not
        if r.status_code == 200:
            updated_msg_format = "Updated \"{}\" to {} {}."

            updated_msg = updated_msg_format.format(manga_title, field_type, new_value)

            if field_type == "status":
                updated_msg = updated_msg_format.format(manga_title, field_type, MANGA_STATUS_MAP[str(new_value)])
            # check if the status was changed
            elif new_status:
                updated_msg += " Status set to \"{}\"".format(MANGA_STATUS_MAP[str(new_status)])

            agent.print_msg(updated_msg)
        else:
            agent.print_msg("There was an error updating the manga. Please try again.")


def search_list(username, search_type, search_string):
    """Search a user's list for a manga or anime and return the matching entry

    :param username: A string, the username of a MAL user
    :param search_type: A string, must be either "anime" or "manga"
    :param search_string: A string, the entry the user wants to update
    :return: A beautiful soup tag or None if unsuccessful
    """

    if search_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(search_type, "anime", "manga"))

    click.echo()

    # the base url of the user list xml data
    url = "https://myanimelist.net/malappinfo.php"

    # send the async request to the server
    r = ui.threaded_action(network.make_request, msg="Searching your {} list".format(search_type), request=requests.get,
                           url=url, params={"u": username, "type": search_type}, stream=True)

    # check if there was an error with the user's internet connection
    if r == network.StatusCode.CONNECTION_ERROR:
        agent.print_connection_error_msg()
        return r

    if r.status_code == 200:
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
            for token in search_string.split():
                if token in series_title_lower or token in series_synonyms_lower:
                    matches.append(entry)
                    break

        num_results = len(matches)

        if num_results == 0:
            agent.print_msg("I could not find \"{}\" on your {} list".format(search_string, search_type))
            return ListSearchStatusCode.NO_RESULTS
        elif num_results == 1:
            return matches[0]
        else:
            agent.print_msg("I found {} results. Did you mean:".format(num_results))

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
            else:
                return ListSearchStatusCode.USER_CANCELLED
    else:
        agent.print_msg("There was an error getting the entry on your list. Please try again.")
        return network.StatusCode.OTHER_ERROR


def view_list(username, search_type):
    """View the anime and manga list of a user

    :param username: A valid MAL username
    :param search_type: A string, must be either "anime" or "manga"
    """

    if search_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(search_type, "anime", "manga"))

    # the base url of the user list xml data
    url = "https://myanimelist.net/malappinfo.php"

    # make the request to the server and get the results
    r = ui.threaded_action(network.make_request, "Getting {} list".format(search_type),
                           request=requests.get, url=url, params={"u": username, "type": search_type}, stream=True)

    # check if there was an error with the user's internet connection
    if r == network.StatusCode.CONNECTION_ERROR:
        agent.print_connection_error_msg()

    elif r.status_code == 200:
        r.raw.decode_content = True

        soup = BeautifulSoup(r.raw, "xml")

        i = 1
        for entry in soup.find_all(search_type):
            # use a different layout depending on whether it is anime or manga
            layout_string = "{}) {}" + "\n    - {}: {}" * (4 if search_type == "anime" else 5)

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
    else:
        agent.print_msg("There was an error getting your {} list. Please try again.".format(search_type))
