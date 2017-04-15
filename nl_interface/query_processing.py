from enum import Enum
import re
import string

import synonyms


class OperationType(Enum):
    """An Enum representing the type of operation the user wants to perform"""
    SEARCH = 0
    UPDATE = 1
    UPDATE_INCREMENT = 2
    ADD = 3
    DELETE = 4
    VIEW_LIST = 5


class UpdateModifier(Enum):
    """An Enum representing the the type of field the user wants to change"""
    STATUS = 0
    SCORE = 1
    EPISODE = 2
    CHAPTER = 3
    VOLUME = 4


class StatusType(Enum):
    WATCHING = 0
    READING = 1
    COMPLETED = 2
    ON_HOLD = 3
    DROPPED = 4
    PLAN_TO_WATCH = 5
    PLAN_TO_READ = 6


class MediaType(Enum):
    """An Enum representing the type of media that an operation applies to"""
    ANIME = 0
    MANGA = 1

class Extras(Enum):
    GREETING = 0
    THANKS = 1
    EXIT = 2


def normalise(query):
    """Normalise a query for consistent string analysis
    
    Convert the query to lowercase and remove punctuation from the right-hand side of the string

    :param query: A string, the user query
    :return: A string, the normalised user query
    """
    return query.lower().rstrip(string.punctuation)


def strip_info(term):
    """Strip a synonym for information from the end of a word

    :param term: A string, the term to remove info from
    :return: A string, the trimmed word or the original if info synonym is not present
    """
    tokens = term.split()

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
    tokens = term.split()
    if tokens[-1] == "anime":
        return term[:-6], MediaType.ANIME
    elif tokens[-1] == "manga":
        return term[:-6], MediaType.MANGA

    return term, None


def determine_action(query):
    """Determine the intended action of the user
     
     Eliminates the cases where a string may match keywords from multiple action categories
    
    :param query: A string, the normalised user query
    :return: An OperationType enum, the action to perform
    """
    action_term_orders = []

    # loop over all of the action categories
    for action in synonyms.actions.keys():
        # loop over all of the synonyms for that action until we find a match
        for syn in synonyms.actions[action]:
            try:
                index = query.index(syn)
                action_term_orders.append((action, index))
                break
            except ValueError:
                continue

    for info_syn in synonyms.terms["information"]:
        try:
            index = query.index(info_syn)
            action_term_orders.append(("information", index))
            break
        except ValueError:
            continue

    if action_term_orders:
        # sort them by index first, then alphabetically
        action_term_orders = sorted(action_term_orders, key=lambda x: (x[1], x[0]))
        if len(action_term_orders) == 2:
            # check if the two lowest indices are the same
            # this will happen if the same keyword exists in two categories
            if action_term_orders[0][1] == action_term_orders[1][1]:
                if action_term_orders[0][0] == "delete" and action_term_orders[1][0] == "search":
                    return OperationType.DELETE

                if action_term_orders[0][0] == "increment" and action_term_orders[1][0] == "update":
                    return OperationType.UPDATE

                if action_term_orders[0][0] == "search" and action_term_orders[1][0] == "view_list":
                    if query.split()[-1] == "list":
                        return OperationType.VIEW_LIST
                    else:
                        return OperationType.SEARCH

        elif len(action_term_orders) == 3:
            if action_term_orders[0][0] == "search" and action_term_orders[1][0] == "update" and action_term_orders[2][0] == "view_list":
                if query.split()[-1] == "list":
                    return OperationType.VIEW_LIST
                else:
                    return OperationType.SEARCH

        string_to_operation_map = {
            "search": OperationType.SEARCH,
            "information": OperationType.SEARCH,
            "update": OperationType.UPDATE,
            "increment": OperationType.UPDATE_INCREMENT,
            "add": OperationType.ADD,
            "delete": OperationType.DELETE,
            "view_list": OperationType.VIEW_LIST
        }

        return string_to_operation_map[action_term_orders[0][0]]


def process(query):
    """Process the user query and return a dictionary with the result

    :param query: A string, the user query
    :return: A dictionary, the result of the query processing
    """
    query = normalise(query)

    if query in synonyms.terms["exit"]:
        return Extras.EXIT

    result = {"operation": None,
              "type": MediaType.ANIME,
              "term": "",
              "modifier": None,
              "value": None,
              "extra": None}

    if re.search("(?:{}).*".format("|".join(synonyms.terms["hello"])), query):
        result["extra"] = Extras.GREETING
    elif re.search("(?:{}).*".format("|".join(synonyms.terms["thank you"])), query):
        result["extra"] = Extras.THANKS

    # determine the likely type of action the user intended
    action = determine_action(query)

    if action == OperationType.SEARCH:
        # rules for search requests

        search_syns = "|".join(synonyms.actions["search"])
        info_syns = "|".join(synonyms.terms["information"])

        sm1 = re.search("(?:{}) (?:(?:for|on) (?:the )?)?(?:{}) (?:(?:for|on) (?:the )?)?(.+)".format(
                        search_syns, info_syns), query)
        sm2 = re.search("(?:{}) (?:(?:for|on) )?(?:the )?(.+)".format(search_syns + "|" + info_syns), query)
        sm3 = re.search("(?:{}) (.+)".format(search_syns), query)

        if sm1 or sm2 or sm3:
            result["operation"] = OperationType.SEARCH
            search_term = ""
            if sm1:
                search_term = sm1.group(1)
                print("sm1")
            elif sm2:
                search_term = strip_info(sm2.group(1))
                print("sm2")
            elif sm3:
                search_term = strip_info(sm3.group(1))
                print("sm3")

            search_terms_stripped_tuple = strip_type(search_term.strip(" '\""))

            if search_terms_stripped_tuple[1] is not None:
                result["type"] = search_terms_stripped_tuple[1]

            result["term"] = search_terms_stripped_tuple[0]

    elif action == OperationType.ADD:
        # rules for add requests

        add_syns = "|".join(synonyms.actions["add"])

        am1 = re.match(".*(?:{}) (.+?)(?= (?:to )?(?:my )?(anime|manga)? ?list)".format(add_syns), query)
        am2 = re.match(".*(?:{}) (.+)".format(add_syns), query)

        if am1 or am2:
            result["operation"] = OperationType.ADD
            add_term = ""
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

        dm1 = re.match(".*(?:{}) (.+?)(?: (?:off )?(?:from )?(?:my )?(anime|manga)? ?(?:list))".format(delete_syns),
                       query)
        dm2 = re.match(".*(?:{}) (.+)".format(delete_syns), query)

        if dm1 or dm2:
            result["operation"] = OperationType.DELETE
            delete_term = ""
            if dm1:
                print("dm1")
                delete_term = dm1.group(1)
                result["type"] = MediaType.MANGA if dm1.group(2) == "manga" else MediaType.ANIME
            elif dm2:
                print("dm2")
                delete_term = dm2.group(1)

            result["term"] = delete_term.strip(" '\"")

    elif action == OperationType.UPDATE or action == OperationType.UPDATE_INCREMENT:
        update_syns = "|".join(synonyms.actions["update"])

        # increment updates

        increment_syns = "|".join(synonyms.actions["increment"])

        inc1 = re.search("(?:{}) (?:the )?(?:count )?(?:(?:for|on) )?(?:the )?(.+ ?) (anime|manga)"
                         .format(increment_syns), query)
        inc2 = re.search("(?:{}) (?:the )?(?:(episode|ep|chapter|chap|volume|vol)s? )?(?:count )?(?:(?:for|on) )?(.+)"
                         .format(increment_syns), query)

        if inc1 or inc2:
            result["operation"] = OperationType.UPDATE_INCREMENT

            if inc1:
                print("inc1")
                if inc1.group(2) == "manga":
                    result["modifier"] = UpdateModifier.CHAPTER
                    result["type"] = MediaType.MANGA
                else:
                    result["modifier"] = UpdateModifier.EPISODE

                result["term"] = inc1.group(1)

            elif inc2:
                print("inc2")
                if inc2.group(1) in ["chapter", "chap"]:
                    result["modifier"] = UpdateModifier.CHAPTER
                    result["type"] = MediaType.MANGA
                elif inc2.group(1) in ["volume", "vol"]:
                    result["modifier"] = UpdateModifier.VOLUME
                    result["type"] = MediaType.MANGA
                else:
                    result["modifier"] = UpdateModifier.EPISODE

                result["term"] = inc2.group(2).strip(" '\"")

        # count updates

        cnt1 = re.search("(?:{}) (?:(?:the|my) )?(?:(episode|ep|chapter|chap|volume|vol)s? )?(?:count )?(?:(?:by|to) )?"
                         "(?:(\d+) )(?:(?:for|on) )(.+)".format(update_syns + "|" + increment_syns), query)
        cnt2 = re.search("(?:{}) (?:(?:the|my) )?(?:(episode|ep|chapter|chap|volume|vol)s? )?(?:count )?"
                         "(?:(?:for|on) )?(.+?) (?:to )?(\d+)".format(update_syns + "|" + increment_syns), query)
        
        if cnt1 or cnt2:
            result["operation"] = OperationType.UPDATE

            if cnt1:
                print("cnt1")
                if cnt1.group(1) in ["chapter", "chap"]:
                    result["modifier"] = UpdateModifier.CHAPTER
                    result["type"] = MediaType.MANGA
                elif cnt1.group(1) in ["volume", "vol"]:
                    result["modifier"] = UpdateModifier.VOLUME
                    result["type"] = MediaType.MANGA
                else:
                    result["modifier"] = UpdateModifier.EPISODE

                result["term"] = cnt1.group(3).strip(" '\"")
                result["value"] = int(cnt1.group(2))

            elif cnt2:
                print("cnt2")
                if cnt2.group(1) in ["chapter", "chap"]:
                    result["modifier"] = UpdateModifier.CHAPTER
                    result["type"] = MediaType.MANGA
                elif cnt2.group(1) in ["volume", "vol"]:
                    result["modifier"] = UpdateModifier.VOLUME
                    result["type"] = MediaType.MANGA
                else:
                    result["modifier"] = UpdateModifier.EPISODE

                result["term"] = cnt2.group(2).strip(" '\"")
                result["value"] = int(cnt2.group(3))

        # score updates

        score_syns = "|".join(synonyms.terms["score"])

        scu1 = re.search("(?:{0}) (?:(?:the|my) )?(?:(?:{1}) )(?:(?:on|of) )?(?:the )?(?:({2}) )?(.+?) (?:({2}) )?"
                         "(?:(?:to|of) )?(-?\d\d?)".format(update_syns, score_syns, "anime|manga"), query)
        scu2 = re.search("(?:{0}) (?:(?:the|my) )?(?:({2}) )?(.+?) (?:({2}) )?(?:with )?(?:a )?(?:(?:{1}) )"
                         "(?:(?:to|of) )?(-?\d\d?)".format(update_syns, score_syns, "anime|manga"), query)

        if scu1 or scu2:
            result["operation"] = OperationType.UPDATE
            result["modifier"] = UpdateModifier.SCORE
            if scu1:
                print("scu1")
                if scu1.group(1) == "manga" or scu1.group(3) == "manga":
                    result["type"] = MediaType.MANGA
                result["term"] = scu1.group(2).strip(" '\"")
                result["value"] = int(scu1.group(4))
            elif scu2:
                print("scu2")
                if scu2.group(1) == "manga" or scu2.group(3) == "manga":
                    result["type"] = MediaType.MANGA
                result["term"] = scu2.group(2).strip(" '\"")
                result["value"] = int(scu2.group(4))

        # status updates

        status_syns = "|".join(synonyms.terms["status"])

        sts1 = re.search("(?:{0}) (?:(?:the|my) )?(?:({1}) )?(?:(?:on|of) )?(?:({2}) )?(.+?) (?:({2}) )?(?:with )?(?:a "
                         ")?(?:({1}) )?(?:(?:to|of|as) )?(?:be )?(watch(?:ing)?|read(?:ing)?|(?:on-?)? ?hold|completed?"
                         "|finish(?:ed)?|drop(?:ped)?|plan(?:ning)?(?: to (?:watch|read)?)?)"
                         .format(update_syns, status_syns, "anime|manga"), query)

        if sts1:
            result["operation"] = OperationType.UPDATE
            result["modifier"] = UpdateModifier.STATUS
            result["term"] = sts1.group(3).strip(" '\"")

            if sts1.group(2) == "manga" or sts1.group(4) == "manga":
                result["type"] = MediaType.MANGA

            status = sts1.group(6)

            if status in synonyms.terms["watching"]:
                result["value"] = StatusType.WATCHING
                result["type"] = MediaType.ANIME
            elif status in synonyms.terms["reading"]:
                result["value"] = StatusType.READING
                result["type"] = MediaType.MANGA
            elif status in synonyms.terms["on hold"]:
                result["value"] = StatusType.ON_HOLD
            elif status in synonyms.terms["completed"]:
                result["value"] = StatusType.COMPLETED
            elif status in synonyms.terms["dropped"]:
                result["value"] = StatusType.DROPPED
            elif status in synonyms.terms["plan to watch"]:
                result["value"] = StatusType.WATCHING
                result["type"] = MediaType.ANIME
            elif status in synonyms.terms["plan to read"]:
                result["value"] = StatusType.READING
                result["type"] = MediaType.MANGA
            elif status in synonyms.terms["plan"]:
                if result["type"] == MediaType.ANIME:
                    result["value"] = StatusType.PLAN_TO_WATCH
                else:
                    result["value"] = StatusType.PLAN_TO_READ

    elif action == OperationType.VIEW_LIST:
        viewlist_syns = "|".join(synonyms.actions["view_list"])

        vl1 = re.search("(?:{}) (?:my )?(?:(anime|manga) )?(?:list)".format(viewlist_syns), query)

        if vl1:
            result["operation"] = OperationType.VIEW_LIST

            if vl1.group(1) == "manga":
                result["type"] = MediaType.MANGA

    return result
