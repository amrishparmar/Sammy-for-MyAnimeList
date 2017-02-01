import click

def main_menu():
    click.echo("=== MAL CLI Application ===")
    click.echo("1) Search for an anime")
    click.echo("2) Search for a manga")
    click.echo("3) Update your anime list")
    click.echo("4) Update your manga list")
    click.echo("5) Exit application")
    choice = click.prompt("Please choose an option", type=int)
    return choice

if __name__ == "__main__":
    main_menu()
