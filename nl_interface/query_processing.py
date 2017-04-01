import re

# import nltk

from . import synonyms


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
    tokens = result.split()
    if tokens[-1] in synonyms.terms["information"]:
        return " ".join(tokens[:-1])
    else:
        return result


def process(query):
    """

    :param query:
    :return:
    """
    query = normalise(query)

    search_syns = "|".join(synonyms.actions["search"])
    info_syns = "|".join(synonyms.terms["information"])

    sm1 = re.match(".*({}) (?:(?:for|on) )?(?:{}) (?:(?:for|on) )?(.+ ?)+".format(search_syns, info_syns), query)
    sm2 = re.match(".*({}) (?:(?:for|on) )?(.+ ?)+".format(search_syns + info_syns), query)
    sm3 = re.match(".*({}) (.+)".format(search_syns), query)

    if sm1 or sm2 or sm3:
        result = {"operation": "search"}

        if sm1:
            result["term"] = sm1.group(2)
            print("m1")
        elif sm2:
            result["term"] = strip_info(sm2.group(2))
            print("m2")
        elif sm3:
            result["term"] = strip_info(sm3.group(2))
            print("m4")
        return result

    return False
