import requests

import agent
import helpers
import network
import search
import ui


def add_entry(credentials, entry_type, search_string=None, entry=None):
    """Add a new entry to the user's anime or manga list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param entry_type: A string, must be either "anime" or "manga"
    :param search_string: A string, the anime or manga the user wants to add to their list
    :param entry: A beautiful soup tag, an entry to add
    :return: None, if the user cancelled
    """

    if entry_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(entry_type, "anime", "manga"))

    if entry is None and search_string is None:
        raise ValueError("Invalid argument combination. Both search_string and entry cannot be None.")

    if entry is None and search_string is not None:
        # search the database for the anime/manga the user wants added
        entry = search.search(credentials, entry_type, search_string, display_details=False)

        if entry == search.StatusCode.NO_RESULTS or entry == search.StatusCode.USER_CANCELLED \
                or entry == network.StatusCode.CONNECTION_ERROR:
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

        # prepare the url
        url = "https://myanimelist.net/api/{}list/add/{}.xml".format(entry_type, entry.id.get_text())

        # send the async add request to the server
        r = ui.threaded_action(network.make_request, msg="Adding", request=requests.get, url=url, params={"data": xml},
                               auth=credentials)

        if r == network.StatusCode.CONNECTION_ERROR:
            agent.print_connection_error_msg()
            return

        # inform the user whether the request was successful or not
        if r.status_code == 201:
            agent.print_msg("I successfully added \"{}\" to your {} list".format(entry.title.get_text(), entry_type))
        else:
            agent.print_msg("I'm sorry, there was an error adding that to your list. {}".format(r.text))
