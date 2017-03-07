import click
import requests
import search
import helpers


def add_entry(credentials, entry_type, entry=None):
    """Add a new entry to the user's anime or manga

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    :param entry_type: A string, must be either "anime" or "manga"
    :param entry: A beautiful soup tag, an entry to add
    :return: None, if the user cancelled
    """

    if entry_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(entry_type, "anime", "manga"))

    # search for the entry to add if one wasn't passed in
    while entry is None:
        click.echo("Search for the entry you wish to add")
        entry = search.search(credentials, entry_type)

        if entry is not None:
            break

        if not click.confirm("Try searching again?"):
            return

    xml_tag_format = "<{0}>{1}</{0}>"
    xml_field_tags = ""

    # get the choice of status
    status = helpers.get_status_choice_from_user(entry_type)

    if status != 6:
        # append the status tag to our xml string if the user didn't opt to skip
        xml_field_tags += xml_tag_format.format("status", status)

        if entry_type == "anime":
            # get the choice of episode count
            episodes = helpers.get_new_count_from_user("episode", int(entry.episodes.get_text()))
            # append
            if episodes is not None:
                xml_field_tags += xml_tag_format.format("episode", episodes)
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

    click.pause()


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
