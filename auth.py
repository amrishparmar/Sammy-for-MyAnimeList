import requests
import click


def _get_user_credentials():
    username = click.prompt("Please enter your MAL Username")
    password = click.prompt("Please enter your password", hide_input=True)
    return username, password


def authenticate_user():
    credentials = _get_user_credentials()
    r = requests.get("https://myanimelist.net/api/account/verify_credentials.xml", auth=credentials)

    if r.status_code == 200:
        click.echo("Authenticated")
        return credentials

    if r.status_code == 401:
        click.echo("Incorrect username or password")
    else:
        click.echo("Error: {}, {}".format(r.status_code, r.text))

    if click.confirm("Try again?"):
        authenticate_user()
    else:
        return False
