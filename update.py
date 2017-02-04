import click
import requests
from bs4 import BeautifulSoup


def increment_episode_count(credentials):
    result = search_list(credentials[0], "anime")

    if result is not None:
        anime_entry, list_data_xml = result

        anime_id = anime_entry.series_animedb_id.get_text()

        current_ep_count = 0
        anime_title = ""

        for entry in list_data_xml.find_all("anime"):
            if entry.series_animedb_id.get_text() == anime_id:
                current_ep_count = int(entry.my_watched_episodes.get_text())
                anime_title = entry.series_title.get_text()

        xml = """<?xml version="1.0" encoding="UTF-8"?><entry><episode>{}</episode></entry>""".format(current_ep_count + 1)

        r = requests.get("https://myanimelist.net/api/animelist/update/{}.xml?data={}".format(anime_id, xml),
                         auth=credentials)

        if r.status_code == 200:
            click.echo("Updated \"{}\" to episode {}".format(anime_title, current_ep_count + 1))
        else:
            click.echo("Error updating anime. Please try again.")

    click.pause()


def increment_chapter_count(credentials):
    result = search_list(credentials[0], "manga")

    if result is not None:
        manga_entry, list_data_xml = result

        manga_id = manga_entry.series_mangadb_id.get_text()

        current_chapter_count = 0
        manga_title = ""

        for entry in list_data_xml.find_all("manga"):
            if entry.series_mangadb_id.get_text() == manga_id:
                current_chapter_count = int(entry.my_read_chapters.get_text())
                manga_title = entry.series_title.get_text()

        xml = """<?xml version="1.0" encoding="UTF-8"?><entry><chapter>{}</chapter></entry>""".format(current_chapter_count + 1)

        r = requests.get("https://myanimelist.net/api/mangalist/update/{}.xml?data={}".format(manga_id, xml),
                         auth=credentials)

        if r.status_code == 200:
            click.echo("Updated \"{}\" to chapter {}".format(manga_title, current_chapter_count + 1))
        else:
            click.echo("Error updating manga. Please try again.")

    click.pause()


def increment_volume_count(credentials):
    manga_id, list_data_xml = search_list(credentials[0], "manga")

    current_volume_count = 0
    manga_title = ""

    for entry in list_data_xml.find_all("manga"):
        if entry.series_mangadb_id.get_text() == manga_id:
            current_volume_count = int(entry.my_read_volumes.get_text())
            manga_title = entry.series_title.get_text()

    xml = """<?xml version="1.0" encoding="UTF-8"?><entry><volume>{}</volume></entry>""".format(current_volume_count + 1)

    r = requests.get("https://myanimelist.net/api/mangalist/update/{}.xml?data={}".format(manga_id, xml),
                     auth=credentials)

    if r.status_code == 200:
        click.echo("Updated \"{}\" to volume {}".format(manga_title, current_volume_count + 1))
    else:
        click.echo("Error updating manga. Please try again.")

    click.pause()


def search_list(username, search_type):

    search_string = click.prompt("Enter name of {} to update".format(search_type))

    search_string = search_string.lower()

    search_tokens = [token.lower() for token in search_string.split()]

    malappinfo = "https://myanimelist.net/malappinfo.php"

    r = requests.get(malappinfo, params={"u": username, "type": search_type}, stream=True)
    r.raw.decode_content = True

    soup = BeautifulSoup(r.raw, "xml")

    matches = []

    for entry in soup.find_all(search_type):
        series_title_lower = entry.series_title.get_text().lower()
        series_synonyms_lower = entry.series_synonyms.get_text().lower()

        if search_string in series_title_lower or search_string in series_synonyms_lower:
            matches.append(entry)
            continue

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
        # counter for labelling each element in the list
        i = 1
        for match in matches:
            # use a different layout for entries that don't have any synonyms
            title_format = "{}> {} ({})" if match.series_synonyms.get_text() != "" else "{}> {}"
            click.echo(title_format.format(i, match.series_title.get_text(), match.series_synonyms.get_text()))
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
            return matches[option - 1], soup
