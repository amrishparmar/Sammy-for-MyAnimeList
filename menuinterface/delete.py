import click
import requests

from . import update


def _delete_entry(credentials, entry_type):
    """Delete an entry on the user's anime or manga list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param entry_type: A string, must be either "anime" or "manga"
    """
    if entry_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(entry_type, "anime", "manga"))

    entry = update.search_list(credentials[0], entry_type)

    if entry is not None:
        # confirm that this is what the user intended
        if click.confirm("Are you sure you want to delete {}?".format(entry.series_title.get_text())):
            entry_id = entry.series_animedb_id.get_text() if entry_type == "anime" \
                                                          else entry.series_mangadb_id.get_text()

            # prepare the url and send the delete request to the server
            url = "https://myanimelist.net/api/{}list/delete/{}.xml".format(entry_type, entry_id)
            r = requests.delete(url, auth=credentials)

            # inform the user of the result
            if r.status_code == 200:
                click.echo("{} was successfully deleted.".format(entry.series_title.get_text()))
            else:
                click.echo("Error deleting {}. Please try again.".format(entry_type))
        else:
            click.echo("Operation cancelled. Nothing was deleted.")

        click.pause()


def delete_anime_entry(credentials):
    """Delete an entry on the user's anime list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    _delete_entry(credentials, "anime")


def delete_manga_entry(credentials):
    """Delete an entry on the user's manga list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    _delete_entry(credentials, "manga")
