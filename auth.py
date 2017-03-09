import requests
import click


def _get_user_credentials():
    """Prompts the user to enter their username and password

    :return: A tuple containing strings in the format (username, password)
    """

    click.clear()
    click.echo("MAL Login:")

    # get the username
    username = click.prompt("Please enter your MAL Username")
    # get the password (the characters should be hidden in a POSIX terminal as they are entered)
    password = click.prompt("Please enter your password", hide_input=True)
    return username, password


def authenticate_user():
    """Authenticates a user with MAL

    Connects to the MAL website to check whether a given combination of username/password is valid

    :return: If successful a tuple containing strings in format (username, password), False otherwise
    """

    while True:
        # get the credentials from the user
        credentials = _get_user_credentials()

        try:
            # make a GET request to the server for an xml (we aren't really concerned with the contents though)
            r = requests.get("https://myanimelist.net/api/account/verify_credentials.xml", auth=credentials)
        except requests.exceptions.ConnectionError:
            click.echo("An error occurred when connecting. Please check your internet connection.")
            return False

        if r.status_code == 200:
            # credentials were successfully authenticated
            click.echo("Authenticated")
            return credentials
        elif r.status_code == 401:
            # server returned unauthorised as the credentials were not valid
            click.echo("Incorrect username or password")
        else:
            # some other http error occurred
            click.echo("Error: {}, {}".format(r.status_code, r.text))

        # check if the user wishes to continue trying
        if click.confirm("Try again?"):
            continue
        else:
            return False
