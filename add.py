import click
import requests
from bs4 import BeautifulSoup
import search
import helpers
from constants import ANIME_STATUS_MAP, MANGA_STATUS_MAP


def add_entry(credentials, entry_type, entry=None):

    if entry_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(entry_type, "anime", "manga"))

    while entry is None:
        click.echo("Search for the entry you wish to add")
        entry = search.search(credentials, entry_type)

        if entry is not None:
            break

        if not click.confirm("Try searching again?"):
            return

    status = helpers.get_status_choice_from_user(entry_type)

    xml_tag_format = "<{0}>{1}</{0}>"
    xml_field_tags = ""

    if status != 6:
        xml_field_tags += xml_tag_format.format("status", status)

        if entry_type == "anime":
            episodes = helpers.get_new_count_from_user("episode", int(entry.episodes.get_text()))
            if episodes is not None:
                xml_field_tags += xml_tag_format.format("episode", episodes)
        else:
            chapters = helpers.get_new_count_from_user("chapter", int(entry.chapters.get_text()))
            volumes = helpers.get_new_count_from_user("volume", int(entry.volumes.get_text()))

            if chapters is not None:
                xml_field_tags += xml_tag_format.format("chapter", chapters)
            if volumes is not None:
                xml_field_tags += xml_tag_format.format("volume", volumes)

    score = helpers.get_score_choice_from_user()

    if score is not None:
        xml_field_tags += xml_tag_format.format("score", score)

    xml = '<?xml version="1.0" encoding="UTF-8"?><entry>{}</entry>'.format(xml_field_tags)

    r = requests.get("https://myanimelist.net/api/{}list/add/{}.xml".format(entry_type, entry.id.get_text()),
                     params={"data": xml}, auth=credentials)

    # inform the user whether the request was successful or not
    if r.status_code == 201:
        click.echo("Added \"{}\" to your {}list".format(entry.title.get_text(), entry_type))
    else:
        click.echo("Error adding {}. {}.".format(entry_type, r.text))

    click.pause()


def add_anime_entry(credentials, entry=None):
    add_entry(credentials, "anime", entry)


def add_manga_entry(credentials, entry=None):
    add_entry(credentials, "manga", entry)
