from enum import Enum
import re

import nltk

import synonyms


class OperationType(Enum):
    SEARCH = 0
    UPDATE = 1
    ADD = 2
    DELETE = 3


class MediaType(Enum):
    ANIME = 0
    MANGA = 1


def normalise(query):
    """

    :param query:
    :return:
    """
    return query.lower()


def strip_info(result):
    """Strip a synonym for information from the end of a word

    :param result:
    :return:
    """
    tokens = nltk.word_tokenize(result)

    try:
        index = synonyms.terms["information"].index(tokens[-1])
        return result.rstrip(synonyms.terms["information"][index])
    except ValueError:
        return result


def strip_type(result):
    tokens = nltk.word_tokenize(result)
    if tokens[-1] == "anime":
        return result[:-6], MediaType.ANIME
    elif tokens[-1] == "manga":
        return result[:-6], MediaType.MANGA

    return result, None


def process(query):
    """

    :param query:
    :return:
    """
    query = normalise(query)

    result = {"operation": None,
              "type": MediaType.ANIME,
              "modifier": None,
              "extra": None}

    for word in synonyms.terms["hello"]:
        if word == nltk.word_tokenize(query)[0]:
            result["extra"] = "Hello, {}!"
            break

    search_syns = "|".join(synonyms.actions["search"])
    info_syns = "|".join(synonyms.terms["information"])

    sm1 = re.match(".*({}) (?:(?:for|on) (?:the )?)?(?:{}) (?:(?:for|on) (?:the )?)?(.+ ?)+".format(
                    search_syns, info_syns), query)
    sm2 = re.match(".*({}) (?:(?:for|on) )?(?:the )?(.+ ?)+".format(search_syns + info_syns), query)
    sm3 = re.match(".*({}) (.+)".format(search_syns), query)

    if sm1 or sm2 or sm3:
        result["operation"] = OperationType.SEARCH
        search_terms = ""
        if sm1:
            search_terms = sm1.group(2)
            print("sm1")
        elif sm2:
            search_terms = strip_info(sm2.group(2))
            print("sm2")
        elif sm3:
            search_terms = strip_info(sm3.group(2))
            print("sm3")
        search_terms_stripped = search_terms.strip(" '\"")
        search_terms_stripped_tuple = strip_type(search_terms_stripped)

        if search_terms_stripped_tuple[1] is not None:
            result["type"] = MediaType.MANGA if search_terms_stripped_tuple[1] == "manga" else MediaType.ANIME

        result["term"] = search_terms_stripped_tuple[0]

    add_syns = "|".join(synonyms.actions["add"])

    am1 = re.match(".*(?:{}) (.+?)(?= (?:to )?(?:my )?(anime|manga)? ?list)".format(add_syns), query)
    am2 = re.match(".*(?:{}) (.+)".format(add_syns), query)

    if am1 or am2:
        result["operation"] = OperationType.ADD
        if am1:
            print("am1")
            result["term"] = am1.group(1)
            result["type"] = MediaType.MANGA if am1.group(2) == "manga" else MediaType.ANIME
        elif am2:
            print("am2")
            result["term"] = am2.group(1)

    delete_syns = "|".join(synonyms.actions["delete"])

    dm1 = re.match(".*(?:{}) (.+?)(?: (?:off )?(?:from )?(?:my )?(anime|manga)? ?(?:list))".format(delete_syns), query)
    dm2 = re.match(".*(?:{}) (.+)".format(delete_syns), query)

    if dm1 or dm2:
        result["operation"] = OperationType.DELETE
        if dm1:
            print("dm1")
            result["term"] = dm1.group(1)
            result["type"] = MediaType.MANGA if dm1.group(2) == "manga" else MediaType.ANIME
        elif dm2:
            print("dm2")
            result["term"] = dm2.group(1)

    return result
