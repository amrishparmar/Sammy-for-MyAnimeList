import click

from . import constants


def get_status_choice_from_user(media_type, skip_option=True):
    """Prompt the user for a choice of new status and return it

    :param media_type: A string, the type of media for which the status is being updated, must be "anime" or "manga"
    :param skip_option:
    :return: An integer, the new status or None if the user cancelled
    """
    if media_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(media_type, "anime", "manga"))

    # select the appropriate map
    status_map = constants.ANIME_STATUS_MAP if media_type == "anime" else constants.MANGA_STATUS_MAP

    click.echo("Which of the following statuses do you want to update to?")

    # print out the list of valid statuses
    for i in range(1, len(status_map.keys()) + 1):
        click.echo("{}> {}".format(i, status_map[str(i) if i != 5 else "6"]))

    # get the number corresponding to the last option
    last_option = int(list(status_map.keys())[-1])

    if skip_option:
        # print out the option to choose none of the statuses
        click.echo("{}> [{}]".format(last_option, "Skip"))

    # get a valid choice from the user
    while True:
        status = click.prompt("Choose an option", type=int)

        # if the user chose a valid status
        if 0 < status < last_option:
            return status + 1 if status == 5 else status  # remap choice of 5 to 6 if chosen
        # if the user cancelled
        elif status == last_option and skip_option:
            return
        else:
            max_value = last_option if skip_option else last_option - 1
            click.echo("You must enter a value between 1 and {}.".format(max_value))


def get_score_choice_from_user():
    """Prompt the user for a new score and return it

    :return: An integer, the new score or None if the user cancelled
    """
    while True:
        score = click.prompt("Enter the new score (leave blank to skip)", default=-1, show_default=False)

        # ensure that the score is an int between 1 and 10 (inclusive)
        if 0 < score < 11:
            return score
        # if the user cancelled
        elif score == -1:
            return
        else:
            click.echo("You must enter a value between 1 and 10.")


def get_new_count_from_user(field_type, limit=0):
    """Prompt the user for a new episode/chapter/volume count and return it

    :param field_type: A string,
    :param limit: An integer, the number of episodes/chapters/volumes in a series
    :return: An integer, the new episode count or None if the user cancelled
    """
    if limit < 0:
        raise ValueError("Limit must be greater than or equal to 0")

    while True:
        count = click.prompt("Enter the new {} count (leave blank to skip)".format(field_type), default=-1,
                             show_default=False)

        if 0 <= count:
            # if there is no limit or there is a valid count
            if limit == 0 or count <= limit:
                return count
        # if the user cancelled
        elif count == -1:
            return

        if limit != 0:
            click.echo("You must enter a value between 0 and {}.".format(limit))
        else:
            click.echo("You must enter a value greater than or equal to 0.")
