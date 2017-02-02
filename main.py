import menus
import auth
import click


def main():
    """Main function"""
    credentials = auth.authenticate_user()

    if credentials:
        menus.main_menu(credentials)

    click.echo("Bye!")

if __name__ == '__main__':
    main()
