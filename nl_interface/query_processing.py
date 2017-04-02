import re

import nltk

import synonyms

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
        return result[:-6], "anime"
    elif tokens[-1] == "manga":
        return result[:-6], "manga"

    return result, None


def process(query):
    """

    :param query:
    :return:
    """
    query = normalise(query)
    result = {"operation": None, "type": "anime"}

    search_syns = "|".join(synonyms.actions["search"])
    info_syns = "|".join(synonyms.terms["information"])

    sm1 = re.match(".*({}) (?:(?:for|on) (?:the )?)?(?:{}) (?:(?:for|on) (?:the )?)?(.+ ?)+".format(
                    search_syns, info_syns), query)
    sm2 = re.match(".*({}) (?:(?:for|on) )?(?:the )?(.+ ?)+".format(search_syns + info_syns), query)
    sm3 = re.match(".*({}) (.+)".format(search_syns), query)

    if sm1 or sm2 or sm3:
        result["operation"] = "search"
        search_terms = ""
        if sm1:
            search_terms = sm1.group(2)
            print("m1")
        elif sm2:
            search_terms = strip_info(sm2.group(2))
            print("m2")
        elif sm3:
            search_terms = strip_info(sm3.group(2))
            print("m4")
        search_terms_stripped = search_terms.strip(" '\"")
        search_terms_stripped_tuple = strip_type(search_terms_stripped)

        if search_terms_stripped_tuple[1] is not None:
            result["type"] = search_terms_stripped_tuple[1]

        result["term"] = search_terms_stripped_tuple[0]

        return result

    return False
