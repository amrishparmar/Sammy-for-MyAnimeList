import click
import sys


def main_menu():
    click.clear()
    click.echo("===== MAL CLI Application =====")
    click.echo("1) Search for an anime")
    click.echo("2) Search for a manga")
    click.echo("3) Update your anime list")
    click.echo("4) Update your manga list")
    click.echo("0) Exit application")
    choice = click.prompt("Please choose an option", type=int)
    _mm_mapping[choice]()


def update_anime_menu():
    click.clear()
    click.echo("===== MAL CLI Application =====")
    click.echo("--- Update your anime list ---")
    click.echo("1) Add new anime")
    click.echo("2) Quick increment episode count for existing anime")
    click.echo("3) Set episode count for existing anime")
    click.echo("4) Set score for existing anime")
    click.echo("5) Set status for existing anime")
    click.echo("9) Go back to main menu")
    choice = click.prompt("Please choose an option", type=int)
    _update_anime_mapping[choice]()


def update_manga_menu():
    click.clear()
    click.echo("===== MAL CLI Application =====")
    click.echo("1) Add new manga")
    click.echo("2) Quick increment chapter count for existing manga")
    click.echo("3) Quick increment volume count for existing manga")
    click.echo("4) Set chapter count for existing manga")
    click.echo("5) Set volume count for existing manga")
    click.echo("6) Set score for existing manga")
    click.echo("7) Set status for existing manga")
    click.echo("9) Go back to main menu")
    choice = click.prompt("Please choose an option", type=int)
    _update_manga_mapping[choice]()


_mm_mapping = {
    1: None,
    2: None,
    3: update_anime_menu,
    4: update_manga_menu,
    0: sys.exit
}

_update_anime_mapping = {
    1: None,
    2: None,
    3: None,
    4: None,
    5: None,
    9: main_menu,
}

_update_manga_mapping = {
    1: None,
    2: None,
    3: None,
    4: None,
    5: None,
    6: None,
    7: None,
    9: main_menu,
}


if __name__ == "__main__":
    main_menu()
