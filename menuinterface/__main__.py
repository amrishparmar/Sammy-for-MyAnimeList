import click

import menus
import auth


def main():
    """Main function"""

    click.clear()

    credentials = auth.authenticate_user()

    if credentials:
        menus.main_menu(credentials)

    click.echo("Bye!")

if __name__ == '__main__':
    main()
