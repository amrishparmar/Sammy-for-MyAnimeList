import click
import requests

import agent
import ui
import update


def delete_entry(credentials, entry_type, search_string):
    """Delete an entry on the user's anime or manga list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param entry_type: A string, must be either "anime" or "manga"
    :param search_string: A string, the entry the user wants to delete
    """
    if entry_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(entry_type, "anime", "manga"))

    entry = update.search_list(credentials[0], entry_type, search_string)

    if entry is not None and \
       entry != update.ListSearchStatusCode.USER_CANCELLED and entry != update.ListSearchStatusCode.NO_RESULTS:

            # confirm that this is what the user intended
            if click.confirm("Sammy> Are you sure you want to delete \"{}\" from your {} list?".format(
                             entry.series_title.get_text(), entry_type)):

                entry_id = entry.series_animedb_id.get_text() if entry_type == "anime" \
                                                              else entry.series_mangadb_id.get_text()

                # prepare the url
                url = "https://myanimelist.net/api/{}list/delete/{}.xml".format(entry_type, entry_id)

                # send the async delete request to the server
                r = ui.threaded_action(requests.delete, "Deleting", **{"url": url, "auth": credentials})

                # inform the user of the result
                if r.status_code == 200:
                    agent.print_msg("I have successfully deleted \"{}\" from your {} list.".format(
                                    entry.series_title.get_text(), entry_type))
                else:
                    agent.print_msg("I'm sorry there was an error deleting \"{}\". {}".format(
                                    entry.series_title.get_text(), r.text()))
            else:
                agent.print_msg("The delete operation was cancelled. Nothing was removed from your {} list.".format(
                                entry_type))

