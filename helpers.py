import click
import constants


def get_status_choice_from_user(media_type, none_option=None):
    if media_type not in ["anime", "manga"]:
        raise ValueError("Invalid argument for {}, must be either {} or {}.".format(media_type, "anime", "manga"))

    status_map = constants.ANIME_STATUS_MAP if media_type == "anime" else constants.MANGA_STATUS_MAP

    click.echo("Which of the following statuses do you want to update to?")

    # print out the list of valid statuses
    for i in range(1, len(status_map.keys()) + 1):
        click.echo("{}> {}".format(i, status_map[str(i) if i != 5 else "6"]))

    # get the number corresponding to the last option
    last_option = int(list(status_map.keys())[-1])

    click.echo("{}> [{}]".format(last_option, none_option or "Cancel"))

    # get a valid choice from the user
    while True:
        status = click.prompt("Choose an option", type=int)

        if 0 < status < last_option:
            return status
        # if user chose to cancel
        elif status == last_option:
            return
        else:
            click.echo("You must enter a value between 1 and {}.".format(last_option))


def get_score_choice_from_user():
    while True:
        score = click.prompt("Enter the new score (Enter -1 to cancel)", type=int)

        # ensure that the score is an int between 1 and 10 (inclusive)
        if 0 < score < 11:
            return score
        elif score == -1:
            return
        else:
            click.echo("You must enter a value between 1 and 10.")


def get_new_count_from_user(field_type, limit=0):
    if limit < 0:
        raise ValueError("Limit must be greater than or equal to 0")

    while True:
        count = click.prompt("Enter the new {} count (Enter -1 to cancel)".format(field_type), type=int)

        if 0 <= count:
            if limit == 0 or count <= limit:
                return count
        elif count == -1:
            return

        if limit != 0:
            click.echo("You must enter a value between 0 and {}.".format(limit))
        else:
            click.echo("You must enter a value greater than or equal to 0.")
