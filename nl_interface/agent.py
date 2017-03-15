import click

from . import auth

credentials = None


def print_msg(msg):
    click.echo("Sammy> " + msg)


def authorise_user():
    global credentials
    while True:
        credentials = auth.get_user_credentials("Please enter your username", "And now your password")

        result = auth.authenticate_user(credentials)

        if type(result) is not tuple:
            if result == auth.StatusCode.CONNECTION_ERROR:
                print_msg("Oh no, there was an error connecting to MAL. Maybe check your internet connection")
            elif result == auth.StatusCode.UNAUTHORISED:
                print_msg("Something was wrong with the username or password :(")
            elif result == auth.StatusCode.OTHER:
                print_msg("Some kind of error has occurred :'(")

            if click.confirm("Sammy> Do you want to try again?"):
                continue
            else:
                return False

        return True


def welcome():
    click.clear()
    click.echo("====== MAL Natural Language Interface ======")
    click.echo()
    print_msg("Hello! My name is Sammy and I am your MyAnimeList digital assistant.")
    print_msg("Before we get started, I need you to confirm your MAL account details.")
    click.echo()

    if authorise_user():
        click.echo()
        print_msg("Yay, everything checked out!")
        print_msg("Let's get started.")
        print_msg("What can I do for you today?")
        return get_query()
    else:
        print_msg("Bye bye!")


def process_query(query):
    print_msg("I'm sorry. I'm not sure what you mean.")


def get_query():
    while True:
        click.echo()
        query = click.prompt(credentials[0], prompt_suffix="> ")
        click.echo()

        if query in ["exit", "quit", "leave"]:
            return

        process_query(query)
