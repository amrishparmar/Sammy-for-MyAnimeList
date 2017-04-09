from enum import Enum
import re

import nltk

import synonyms


class OperationType(Enum):
    """An Enum represented the type of operation the user wants to perform"""
    SEARCH = 0
    UPDATE = 1
    UPDATE_INCREMENT = 2
    ADD = 3
    DELETE = 4


class UpdateModifier(Enum):
    STATUS = 0
    SCORE = 1
    EPISODE = 2
    CHAPTER = 3
    VOLUME = 4


class MediaType(Enum):
    """An Enum represented the type of media that an operation applies to"""
    ANIME = 0
    MANGA = 1

string_to_operation_map = {
    "search": OperationType.SEARCH,
    "update": OperationType.UPDATE,
    "increment": OperationType.UPDATE_INCREMENT,
    "add": OperationType.ADD,
    "delete": OperationType.DELETE
}


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


def determine_action(query):
    action_term_orders = []

    for action in synonyms.actions.keys():
        for syn in synonyms.actions[action]:
            try:
                index = query.index(syn)
                action_term_orders.append((action, index))
                break
            except ValueError:
                continue

    if not action_term_orders:
        # the query did not match any of our known keywords
        return None
    else:
        action_term_orders = sorted(action_term_orders, key=lambda x: (x[1], x[0]))
        if len(action_term_orders) >= 2:
            if action_term_orders[0][1] == action_term_orders[1][1]:
                if action_term_orders[0][0] == "delete" and action_term_orders[1][0] == "search":
                    return string_to_operation_map["delete"]

                if action_term_orders[0][0] == "increment" and action_term_orders[1][0] == "update":
                    return string_to_operation_map["update"]

        return string_to_operation_map[action_term_orders[0][0]]


def process(query):
    """Process the user query and return a dictionary with the result

    :param query: A string, the user query
    :return: A dictionary, the result of the query processing
    """
    query = normalise(query)

    result = {"operation": None,
              "type": MediaType.ANIME,
              "modifier": None,
              "value": None,
              "extra": None}

    # basic implementation of responding to hello
    for word in synonyms.terms["hello"]:
        if word == nltk.word_tokenize(query)[0]:
            result["extra"] = "Hello, {}!"
            break

    # determine the likely type of action the user intended
    action = determine_action(query)

    if action == OperationType.SEARCH:
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

    elif action == OperationType.ADD:
        # rules for add requests

        add_syns = "|".join(synonyms.actions["add"])

        am1 = re.match(".*(?:{}) (.+?)(?= (?:to )?(?:my )?(anime|manga)? ?list)".format(add_syns), query)
        am2 = re.match(".*(?:{}) (.+)".format(add_syns), query)

        add_term = ""

        if am1 or am2:
            result["operation"] = OperationType.ADD
            if am1:
                print("am1")
                add_term = am1.group(1)
                result["type"] = MediaType.MANGA if am1.group(2) == "manga" else MediaType.ANIME
            elif am2:
                print("am2")
                add_term = am2.group(1)

            result["term"] = add_term.strip(" '\"")

    elif action == OperationType.DELETE:
        delete_syns = "|".join(synonyms.actions["delete"])

        dm1 = re.match(".*(?:{}) (.+?)(?: (?:off )?(?:from )?(?:my )?(anime|manga)? ?(?:list))".format(delete_syns), query)
        dm2 = re.match(".*(?:{}) (.+)".format(delete_syns), query)

        delete_term = ""

        if dm1 or dm2:
            result["operation"] = OperationType.DELETE
            if dm1:
                print("dm1")
                delete_term = dm1.group(1)
                result["type"] = MediaType.MANGA if dm1.group(2) == "manga" else MediaType.ANIME
            elif dm2:
                print("dm2")
                delete_term = dm2.group(1)

            result["term"] = delete_term.strip(" '\"")

    elif action == OperationType.UPDATE or action == OperationType.UPDATE_INCREMENT:
        increment_syns = "|".join(synonyms.actions["increment"])

        inc1 = re.match(".*(?:{}) (?:the )?(?:(episode|chapter|volume)s? )?(?:count )?(?:for |on )?(.+ ?)+?".format(
                            increment_syns), query)

        if inc1:
            result["operation"] = OperationType.UPDATE_INCREMENT
            result["type"] = MediaType.MANGA
            increment_term = inc1.group(2)

            if inc1.group(1) == "chapter":
                modifier_term = UpdateModifier.CHAPTER
            elif inc1.group(1) == "volume":
                modifier_term = UpdateModifier.VOLUME
            else:
                modifier_term = UpdateModifier.EPISODE
                result["type"] = MediaType.ANIME

            result["modifier"] = modifier_term
            result["term"] = increment_term

    return result
