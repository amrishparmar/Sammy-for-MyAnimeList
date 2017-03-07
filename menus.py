import click
import search
import update
import add


def menu_heading(username, submenu=None):
    """Heading for all menus

    :param username: a string containing the username of the authenticated user
    :param submenu: a string with the name of submenu
    """
    click.clear()
    click.secho("===== MAL CLI Application =====", fg="white", bg="blue")
    click.echo("Logged in as: " + click.style("{}\n".format(username), fg="yellow", bg="cyan"))
    if submenu is not None:
        click.echo("--- Update your {} list ---".format(submenu))


def main_menu(credentials):
    """Main main for program

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """

    # loop lets the program run until user decides to quit
    while True:
        menu_heading(credentials[0])
        click.echo("1) Search for an anime")
        click.echo("2) Search for a manga")
        click.echo("3) Update your anime list")
        click.echo("4) Update your manga list")
        click.echo("0) Exit application")

        # get a choice for the user
        choice = click.prompt("Please choose an option", type=int)

        if choice in range(1, 5):
            _mm_mapping[choice](credentials)
        elif choice == 0:
            return


def update_anime_menu(credentials):
    """Menu with options for updating user anime list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    while True:
        menu_heading(credentials[0], submenu="anime")
        click.echo("1) View my anime list")
        click.echo("2) Add new anime")
        click.echo("3) Quick increment episode count for existing anime")
        click.echo("4) Set episode count for existing anime")
        click.echo("5) Set score for existing anime")
        click.echo("6) Set status for existing anime")
        click.echo("9) Go back to main menu")

        choice = click.prompt("Please choose an option", type=int)

        if choice in range(1, 7):
            _update_anime_mapping[choice](credentials)
        elif choice == 9:
            return


def update_manga_menu(credentials):
    """Menu with options for updating user manga list

    :param credentials: A tuple containing valid MAL account details in the format (username, password)
    """
    while True:
        menu_heading(credentials[0], submenu="manga")
        click.echo("1) View my manga list")
        click.echo("2) Add new manga")
        click.echo("3) Quick increment chapter count for existing manga")
        click.echo("4) Quick increment volume count for existing manga")
        click.echo("5) Set chapter count for existing manga")
        click.echo("6) Set volume count for existing manga")
        click.echo("7) Set score for existing manga")
        click.echo("8) Set status for existing manga")
        click.echo("9) Go back to main menu")

        choice = click.prompt("Please choose an option", type=int)

        if choice in range(1, 9):
            _update_manga_mapping[choice](credentials)
        elif choice == 9:
            return

# function mappings for main menu
_mm_mapping = {
    1: search.anime_search,
    2: search.manga_search,
    3: update_anime_menu,
    4: update_manga_menu
}

# function mappings for update anime menu
_update_anime_mapping = {
    1: update.view_anime_list,
    2: add.add_anime_entry,
    3: update.increment_episode_count,
    4: update.set_episode_count,
    5: update.set_anime_score,
    6: update.set_anime_status
}

# function mappings for update manga menu
_update_manga_mapping = {
    1: update.view_manga_list,
    2: add.add_manga_entry,
    3: update.increment_chapter_count,
    4: update.increment_volume_count,
    5: update.set_chapter_count,
    6: update.set_volume_count,
    7: update.set_manga_score,
    8: update.set_manga_status,
}
