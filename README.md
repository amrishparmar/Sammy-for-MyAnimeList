**NOTE: This application does not work due to MALs deactivation of the API**

# Sammy for MyAnimeList
An application for updating and retrieving information from [MyAnimeList.net](https://www.myanimelist.net) (MAL) using natural language queries.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This comprises of two applications: the **natural language interface** and the **menu-driven interface**.

Features common to both of them include:
- Search the MAL database for anime or manga information
- Add new anime or manga to user's personal list
- Delete anime or manga from the user's personal list
- Update episode/chapter/volume information on user's personal list
- Update scores on user's personal list
- Update statuses on user's personal list

The natural language interface allows users to enter commands in plain English to access and update information from the MAL website. For example, the user could enter queries such as `I want to search for Naruto information` for search or `Update my chapter count for Death Note` to increment the number of read chapters on their manga list as well as many others.

The menu-driven interface is also allows users to manage their own personal lists and search the website, however it does not feature natural language functionality.
_N.B. This version doesn't quite have feature parity with the NL interface when it comes to some of underlying functionality, particularly network code. This will likely be improved in future._

## Using the application
### Executable binaries
To run the application, you can download the binary for your platform from the [releases](https://github.com/amrishparmar/mal_cl_interface/releases) page.
### Running from source
#### Dependencies
To run from source, the following are required:
- [Python](https://www.python.org/) v3.4+
- [Requests](http://docs.python-requests.org/en/master/)
- [Click](http://click.pocoo.org/6/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
#### Executing the scripts
For the natural language interface run the following from the root of the project:
```
python nl_interface
```
For the menu-driven interface run the following from the root of the project:
```
python menuinterface
```

You may need to replace `python` with `python3` in the commands above to run the correct version of Python, particularly on some Mac/Linux configurations.

Enjoy! :)
