# MyAnimeList CLI and NL Query Application
An application for updating and retrieving information from [MyAnimeList.net](https://www.myanimelist.net) (MAL) using natural language queries.

This comprises of two applications: the **menu-driven interface** and the **natural language interface**.

Common features of them include:
- Search the MAL database for anime or manga information
- Add new anime or manga to user's personal list
- Delete anime or manga from the user's personal list
- Update episode/chapter/volume information on user's personal list
- Update scores on user's personal list
- Update statuses on user's personal list

The menu-driven interface is a simple command-line application that allows users to manage their own personal lists.

The natural language interface allows users to enter commands in plain English to access and update information from the MAL website. For example, the user could enter queries such as `I want to search for Naruto information` for search or `Update my chapter count for Death Note` to increment the number of read chapters on their manga list as well as many others.

## Using the application
### Dependencies
To run from source, the following are required:
- [Python](https://www.python.org/) v3.4+
- [Requests](http://docs.python-requests.org/en/master/)
- [Click](http://click.pocoo.org/6/) v6+
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) v4
- [Natural Language Toolkit (NLTK)](http://www.nltk.org/) v3 [only required for the natural language interface]

### Running the application
For the menu-driven interface run the following from the root of the project:
```
python menuinterface.py
```
For the natural language interface run the following from the root of the project:
```
python nlinterface.py
```

Enjoy! :)
