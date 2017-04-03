import click
import requests

import agent
import helpers
import search


def add_entry(credentials, entry_type, search_string=None, entry=None):
    """Add a new entry to the user's anime or manga

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param entry_type: A string, must be either "anime" or "manga"
    :param search_string: sdfsdfsdfsdfsd
    :param entry: A beautiful soup tag, an entry to add
    :return: None, if the user cancelled
    """

    if entry_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(entry_type, "anime", "manga"))

    if entry is None and search_string is None:
        raise ValueError("Invalid argument combination. Both search_string and entry cannot be None.")

    if entry is None and search_string is not None:
        entry = search.search(credentials, entry_type, search_string)

        if entry == search.StatusCode.NO_RESULTS:
            return entry
        elif entry == search.StatusCode.USER_CANCELLED:
            return

        xml_tag_format = "<{0}>{1}</{0}>"
        xml_field_tags = ""

        # get the choice of status
        status = helpers.get_status_choice_from_user(entry_type, skip_option=False)

        if status != 6:
            # append the status tag to our xml string if the user didn't opt to skip
            xml_field_tags += xml_tag_format.format("status", status)

            if entry_type == "anime":
                if status == 2:
                    episodes = entry.episodes.get_text()
                else:
                    # get the choice of episode count
                    episodes = helpers.get_new_count_from_user("episode", int(entry.episodes.get_text()))

                # append the episode count if the user didn't opt to skip
                if episodes is not None:
                    xml_field_tags += xml_tag_format.format("episode", episodes)
            else:
                if status == 2:
                    chapters = entry.chapters.get_text()
                    volumes = entry.volumes.get_text()
                else:
                    # get the choice of chapter and volume count
                    chapters = helpers.get_new_count_from_user("chapter", int(entry.chapters.get_text()))
                    volumes = helpers.get_new_count_from_user("volume", int(entry.volumes.get_text()))

                # append chapter and volume choice if the user didn't opt to skip
                if chapters is not None:
                    xml_field_tags += xml_tag_format.format("chapter", chapters)
                if volumes is not None:
                    xml_field_tags += xml_tag_format.format("volume", volumes)

            # get the choice of score
            score = helpers.get_score_choice_from_user()

            # append score choice if the user didn't opt to skip
            if score is not None:
                xml_field_tags += xml_tag_format.format("score", score)

            # form the xml string
            xml = '<?xml version="1.0" encoding="UTF-8"?><entry>{}</entry>'.format(xml_field_tags)

            # make the request to the server to add
            r = requests.get("https://myanimelist.net/api/{}list/add/{}.xml".format(entry_type, entry.id.get_text()),
                             params={"data": xml}, auth=credentials)

            # inform the user whether the request was successful or not
            if r.status_code == 201:
                click.echo("Added \"{}\" to your {}list".format(entry.title.get_text(), entry_type))
            else:
                click.echo("Error adding {}. {}.".format(entry_type, r.text))


def add_anime_entry(credentials, entry=None):
    """Add a new anime entry to the user's anime list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param entry: A beautiful soup tag, an entry to add
    """
    add_entry(credentials, "anime", entry)


def add_manga_entry(credentials, entry=None):
    """Add a new manga entry to the user's manga list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param entry: A beautiful soup tag, an entry to add
    """
    add_entry(credentials, "manga", entry)
