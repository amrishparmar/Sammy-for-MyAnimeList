import click
import search


def menu_heading(submenu=None):
    """Heading for all menus

    :param submenu: String with that name of submenu
    """
    click.clear()
    click.echo("===== MAL CLI Application =====")
    click.echo("Logged in as: TODO\n")
    click.echo()
    if submenu is not None:
        click.echo("--- Update your {} list ---".format(submenu))


def main_menu():
    """Main main for program"""

    # loop lets the program run until user decides to quit
    while True:
        menu_heading()
        click.echo("1) Search for an anime")
        click.echo("2) Search for a manga")
        click.echo("3) Update your anime list")
        click.echo("4) Update your manga list")
        click.echo("0) Exit application")

        # get a choice for the user
        choice = click.prompt("Please choose an option", type=int)

        if choice == 0:
            return
        else:
            # try/except to handle trying to call options that aren't in function map dictionary
            try:
                _mm_mapping[choice]()
            except KeyError:
                continue


def update_anime_menu():
    """Menu with options for updating user anime list"""

    menu_heading(submenu="anime")
    click.echo("1) Add new anime")
    click.echo("2) Quick increment episode count for existing anime")
    click.echo("3) Set episode count for existing anime")
    click.echo("4) Set score for existing anime")
    click.echo("5) Set status for existing anime")
    click.echo("9) Go back to main menu")

    choice = click.prompt("Please choose an option", type=int)

    if choice == 9:
        return
    # _update_anime_mapping[choice]()


def update_manga_menu():
    """Menu with options for updating user manga list"""

    menu_heading(submenu="manga")
    click.echo("--- Update your anime list ---")
    click.echo("1) Add new manga")
    click.echo("2) Quick increment chapter count for existing manga")
    click.echo("3) Quick increment volume count for existing manga")
    click.echo("4) Set chapter count for existing manga")
    click.echo("5) Set volume count for existing manga")
    click.echo("6) Set score for existing manga")
    click.echo("7) Set status for existing manga")
    click.echo("9) Go back to main menu")

    choice = click.prompt("Please choose an option", type=int)

    if choice == 9:
        return
    # _update_manga_mapping[choice]()

# function mappings for main menu
_mm_mapping = {
    1: search.anime_search,
    2: search.manga_search,
    3: update_anime_menu,
    4: update_manga_menu
}

# function mappings for update anime menu
_update_anime_mapping = {
    1: None,
    2: None,
    3: None,
    4: None,
    5: None,
}

# function mappings for update manga menu
_update_manga_mapping = {
    1: None,
    2: None,
    3: None,
    4: None,
    5: None,
    6: None,
    7: None,
}
