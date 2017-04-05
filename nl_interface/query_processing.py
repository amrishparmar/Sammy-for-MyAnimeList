from enum import Enum
import re

import nltk

import synonyms


class OperationType(Enum):
    """An Enum represented the type of operation the user wants to perform"""
    SEARCH = 0
    UPDATE = 1
    ADD = 2
    DELETE = 3


class MediaType(Enum):
    """An Enum represented the type of media that an operation applies to"""
    ANIME = 0
    MANGA = 1


def normalise(query):
    """Normalise a query for consistent string analysis

    :param query: A string, the user query
    :return: A string, the normalised user query
    """
    return query.lower()


def strip_info(term):
    """Strip a synonym for information from the end of a word

    :param term: A string, the term to remove info from
    :return: A string, the trimmed word or the original if info synonym is not present
    """
    tokens = nltk.word_tokenize(term)

    try:
        index = synonyms.terms["information"].index(tokens[-1])
        return term.rstrip(synonyms.terms["information"][index])
    except ValueError:
        return term


def strip_type(term):
    """Remove the word "anime" or "manga" from the end of a string and return the result
    
    :param term: A string, the term to remove media type from
    :return: A tuple (string, MediaType.VALUE), the trimmed word and the type of media 
             or the original and None if no modifications made 
    """
    tokens = nltk.word_tokenize(term)
    if tokens[-1] == "anime":
        return term[:-6], MediaType.ANIME
    elif tokens[-1] == "manga":
        return term[:-6], MediaType.MANGA

    return term, None


def process(query):
    """Process the user query and return a dictionary with the result

    :param query: A string, the user query
    :return: A dictionary, the result of the query processing
    """
    query = normalise(query)

    result = {"operation": None,
              "type": MediaType.ANIME,
              "modifier": None,
              "extra": None}

    # basic implementation of responding to hello
    for word in synonyms.terms["hello"]:
        if word == nltk.word_tokenize(query)[0]:
            result["extra"] = "Hello, {}!"
            break

    # rules for search requests

    search_syns = "|".join(synonyms.actions["search"])
    info_syns = "|".join(synonyms.terms["information"])

    sm1 = re.match(".*(?:{}) (?:(?:for|on) (?:the )?)?(?:{}) (?:(?:for|on) (?:the )?)?(.+ ?)+".format(
                    search_syns, info_syns), query)
    sm2 = re.match(".*(?:{}) (?:(?:for|on) )?(?:the )?(.+ ?)+".format(search_syns + info_syns), query)
    sm3 = re.match(".*(?:{}) (.+)".format(search_syns), query)

    if sm1 or sm2 or sm3:
        result["operation"] = OperationType.SEARCH
        search_terms = ""
        if sm1:
            search_terms = sm1.group(1)
            print("sm1")
        elif sm2:
            search_terms = strip_info(sm2.group(1))
            print("sm2")
        elif sm3:
            search_terms = strip_info(sm3.group(1))
            print("sm3")
        search_terms_stripped = search_terms.strip(" '\"")
        search_terms_stripped_tuple = strip_type(search_terms_stripped)

        if search_terms_stripped_tuple[1] is not None:
            result["type"] = MediaType.MANGA if search_terms_stripped_tuple[1] == "manga" else MediaType.ANIME

        result["term"] = search_terms_stripped_tuple[0]

    # rules for add requests

    add_syns = "|".join(synonyms.actions["add"])

    am1 = re.match(".*(?:{}) (.+?)(?= (?:to )?(?:my )?(anime|manga)? ?list)".format(add_syns), query)
    am2 = re.match(".*(?:{}) (.+)".format(add_syns), query)

    if am1 or am2:
        result["operation"] = OperationType.ADD
        if am1:
            print("am1")
            result["type"] = MediaType.MANGA if am1.group(2) == "manga" else MediaType.ANIME
        elif am2:
            print("am2")

        result["term"] = am1.group(1).strip(" '\"")

    # rules for delete requests

    delete_syns = "|".join(synonyms.actions["delete"])

    dm1 = re.match(".*(?:{}) (.+?)(?: (?:off )?(?:from )?(?:my )?(anime|manga)? ?(?:list))".format(delete_syns), query)
    dm2 = re.match(".*(?:{}) (.+)".format(delete_syns), query)

    if dm1 or dm2:
        result["operation"] = OperationType.DELETE
        if dm1:
            print("dm1")
            result["type"] = MediaType.MANGA if dm1.group(2) == "manga" else MediaType.ANIME
        elif dm2:
            print("dm2")

        result["term"] = am1.group(1).strip(" '\"")

    return result
