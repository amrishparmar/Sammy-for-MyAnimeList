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
    """

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

    m1 = re.match(".*({}) (?:(?:for|on) )?(?:{}) (?:for|on )?(.+ ?)+".format(search_syns, info_syns), query)
    m5 = re.match("(.*?)({}) (?:(?:for|on) )(.+ ?)+".format(info_syns), query)
    m2 = re.match(".*({}) (?:(?:for|on) )(.+ ?) {}".format(search_syns, info_syns), query)
    m3 = re.match(".*({}) (?:(?:for|on) )(.+ ?)+".format(search_syns, info_syns), query)
    m4 = re.match(".*({}) (.+)".format(search_syns), query)

    if m1 or m2 or m3 or m4:
        result = {"operation": "search"}

        if m1:
            result["term"] = m1.group(2)
            print("m1")
        elif m5:
            result["term"] = m5.group(3)
            print("m5")
        elif m2:
            result["term"] = m2.group(2)
            print("m2")
        elif m3:
            result["term"] = strip_info(m3.group(2))
            print("m3")
        elif m4:
            result["term"] = strip_info(m4.group(2))
            print("m4")
        # elif m0:
        #     result["term"] = m0.group(1)
        #     print("m0")
        return result

    return False
