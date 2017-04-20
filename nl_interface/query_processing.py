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
    """An Enum representing the entry status the user want to update to"""
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
    """An Enum for commands that aren't MAL-related"""
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
    # check that we've not passed an empty string
    if not term:
        return term

    # split the query term into tokens
    tokens = term.split()

    try:
        # get the index of a synonym for "information" (raises exception if not in there)
        index = synonyms.terms["information"].index(tokens[-1])
        return " ".join(tokens[:-1])
    except ValueError:
        return term


def strip_type(term):
    """Remove the word "anime" or "manga" from the end of a string and return the result
    
    :param term: A string, the term to remove media type from
    :return: A tuple (string, MediaType.VALUE), the trimmed word and the type of media or the original 
             and None if no modifications made 
    """
    # check that we've not passed an empty string
    if not term:
        return term, None

    # split the query term into tokens
    tokens = term.split()

    if tokens[-1] == "anime":
        return " ".join(tokens[:-1]), MediaType.ANIME
    elif tokens[-1] == "manga":
        return " ".join(tokens[:-1]), MediaType.MANGA

    return term, None


def determine_action(query):
    """Determine the intended action of the user
     
     Eliminates the cases where a string may match keywords from multiple action categories
    
    :param query: A string, the normalised user query
    :return: An OperationType enum, the action to perform
    """
    # a list of tuples with action terms found in the query in the form (action, index of action term)
    action_term_orders = []

    def match_syns(syns, ac):
        """Loop over a list of synonyms and append the index and action to a term orders list if in the query
        
        :param syns: The list of synonyms
        :param ac: A string, the name of the action
        """
        pos_syn = -1
        for syn in syns:
            if syn in query:
                ato_index = query.index(syn)
                if pos_syn == -1:
                    action_term_orders.append((ac, ato_index))
                    pos_syn = len(action_term_orders) - 1
                else:
                    if action_term_orders[pos_syn][1] > ato_index:
                        action_term_orders[pos_syn] = (ac, ato_index)

    # loop over all of the action categories
    for action in synonyms.actions:
        # loop over all of the synonyms for that action until we find a match
        match_syns(synonyms.actions[action], action)

    # loop over the synonyms of information (as can be used as an alias for search)
    match_syns(synonyms.terms["information"], "information")

    if action_term_orders:

        string_to_operation_map = {
            "search": OperationType.SEARCH,
            "information": OperationType.SEARCH,
            "update": OperationType.UPDATE,
            "increment": OperationType.UPDATE,
            "add": OperationType.ADD,
            "delete": OperationType.DELETE,
            "view_list": OperationType.VIEW_LIST
        }

        # sort them by index first, then alphabetically
        action_term_orders = sorted(action_term_orders, key=lambda x: (x[1], x[0]))
        if len(action_term_orders) == 2:
            # check if the two lowest indices are the same
            # this will happen if the same (or part of the same) keyword exists in two categories
            if action_term_orders[0][1] == action_term_orders[1][1]:
                if action_term_orders[0][0] == "delete" and action_term_orders[1][0] == "search":
                    return OperationType.DELETE

                if action_term_orders[0][0] == "search" and action_term_orders[1][0] == "view_list":
                    if query.split()[-1] == "list":
                        return OperationType.VIEW_LIST
                    else:
                        return OperationType.SEARCH

        elif len(action_term_orders) >= 3:
            # check if the three lowest indices are the same
            # this will happen if the same (or part of the same) keyword exists in three categories
            if action_term_orders[0][0] == "search" and action_term_orders[1][0] == "update" \
                    and action_term_orders[2][0] == "view_list":
                if query.split()[-1] == "list":
                    return OperationType.VIEW_LIST
                else:
                    return OperationType.SEARCH
            elif action_term_orders[0][0] == "delete" and action_term_orders[1][0] == "search" \
                    and action_term_orders[2][0] == "view_list":
                if action_term_orders[0][1] <= min([i for (_, i) in action_term_orders]) or "get rid of" in query:
                    return OperationType.DELETE
                else:
                    return OperationType.VIEW_LIST

        return string_to_operation_map[action_term_orders[0][0]]


def process(query):
    """Process the user query and return a dictionary with the result

    :param query: A string, the user query
    :return: A dictionary, the result of the query processing or Extras.EXIT if the user wants to quit
    """
    # normalise the user query
    query = normalise(query)

    # the user wants to quit
    if query in synonyms.terms["exit"]:
        return Extras.EXIT

    # the dictionary that will be returned with all
    result = {
        "operation": None,          # the operation to carry out
        "type": MediaType.ANIME,    # the type of media; anime or manga, default: anime
        "term": "",                 # the search term for the operation type
        "modifier": None,           # a modifier for operation type
        "value": None,              # an additional value to set for the operation
        "extra": None               # extra content, e.g. for greetings
    }

    # the user said hello or thank you
    if re.search("(?:{})".format("|".join(synonyms.terms["hello"])), query):
        result["extra"] = Extras.GREETING
    elif re.search("(?:{})".format("|".join(synonyms.terms["thank you"])), query):
        result["extra"] = Extras.THANKS

    # determine the likely type of action the user intended
    action = determine_action(query)

    if action == OperationType.SEARCH:
        # evaluate query using rules for search requests

        # convert list of search and info syns to a string separated by | chars
        search_syns = "|".join(synonyms.actions["search"])
        info_syns = "|".join(synonyms.terms["information"])

        sm1 = re.search("(?:{}) (?:(?:me|us) )?(?:some )?(?:(?:for|on|of) (?:the )?)?(?:{}) (?:(?:for|on|of) "
                        "(?:the )?)?(.+)".format(search_syns, info_syns), query)
        sm2 = re.search("(?:{}) (?:(?:me|us) )?(?:some )?(?:(?:for|on|of) )?(?:the )?(.+)"
                        .format(search_syns + "|" + info_syns), query)
        sm3 = re.search("(?:{}) (.+)".format(search_syns), query)

        # if one of the rules matched
        if sm1 or sm2 or sm3:
            result["operation"] = OperationType.SEARCH

            if sm1:
                search_term = sm1.group(1)
            elif sm2:
                search_term = strip_info(sm2.group(1))
            else:
                search_term = strip_info(sm3.group(1))

            # remove quotes or spaces from the term and get the media type
            search_terms_stripped_tuple = strip_type(search_term.strip(" '\""))

            # if there was a valid media type
            if search_terms_stripped_tuple[1] is not None:
                result["type"] = search_terms_stripped_tuple[1]

            result["term"] = search_terms_stripped_tuple[0]

    elif action == OperationType.ADD:
        # evaluate query using rules for add requests

        # convert list of add syns to a string separated by | chars
        add_syns = "|".join(synonyms.actions["add"])

        am1 = re.search("(?:{}) (?:the )?(.+?)(?: (?:(?:onto|to|on) )?(?:my )?(anime|manga))".format(add_syns), query)
        am2 = re.search("(?:{}) (?:the )?(.+?)(?: (?:(?:onto|to|on) )?(?:my )?(anime|manga)? ?list)"
                        .format(add_syns), query)
        am3 = re.search("(?:{}) (.+)".format(add_syns), query)

        # if one of the rules matched
        if am1 or am2 or am3:
            result["operation"] = OperationType.ADD

            if am1:
                add_term = am1.group(1)
                result["type"] = MediaType.MANGA if am1.group(2) == "manga" else MediaType.ANIME
            elif am2:
                add_term = am2.group(1)
                result["type"] = MediaType.MANGA if am2.group(2) == "manga" else MediaType.ANIME
            else:
                add_term = am3.group(1)

            result["term"] = add_term.strip(" '\"")

    elif action == OperationType.DELETE:
        # evaluate query using rules for delete requests

        # convert list of add syns to a string separated by | chars
        delete_syns = "|".join(synonyms.actions["delete"])

        dm1 = re.search("(?:{}) (?:the )?(.+?)(?: (?:off )?(?:(?:from|of) )?(?:my )?(anime|manga))".format(delete_syns),
                        query)
        dm2 = re.search("(?:{}) (?:the )?(.+?)(?: (?:off )?(?:(?:from|of) )?(?:my )?(anime|manga)? ?list)"
                        .format(delete_syns), query)
        dm3 = re.search("(?:{}) (.+)".format(delete_syns), query)

        # if one of the rules matched
        if dm1 or dm2 or dm3:
            result["operation"] = OperationType.DELETE

            def assign_delete_vals(type_group, term_group):
                """Assign the type and term of the match groups to result"""
                result["type"] = MediaType.MANGA if type_group == "manga" else MediaType.ANIME
                result["term"] = term_group.strip(" '\"")

            if dm1:
                assign_delete_vals(dm1.group(2), dm1.group(1))
            elif dm2:
                assign_delete_vals(dm2.group(2), dm2.group(1))
            else:
                assign_delete_vals("anime", dm3.group(1))

    elif action == OperationType.UPDATE:
        # evaluate query using rules for update requests

        # convert list of update syns to a string separated by | chars
        update_syns = "|".join(synonyms.actions["update"])

        # increment updates

        # convert list of increment syns to a string separated by | chars
        increment_syns = "|".join(synonyms.actions["increment"])

        inc1 = re.search("(?:{}) (?:the )?(?:count )?(?:(?:for|on) )?(?:the )?(.+ ?) (anime|manga)"
                         .format(increment_syns), query)
        inc2 = re.search("(?:{}) (?:the )?(?:(episode|ep|chapter|chap|volume|vol)s? )?(?:count )?(?:(?:for|on) )?(.+)"
                         .format(increment_syns), query)

        # if one of the rules matched
        if inc1 or inc2:
            result["operation"] = OperationType.UPDATE_INCREMENT

            if inc1:
                if inc1.group(2) == "manga":
                    result["modifier"] = UpdateModifier.CHAPTER
                    result["type"] = MediaType.MANGA
                else:
                    result["modifier"] = UpdateModifier.EPISODE

                result["term"] = inc1.group(1).strip(" '\"")

            elif inc2:
                if inc2.group(1) in synonyms.terms["chapter"]:
                    result["modifier"] = UpdateModifier.CHAPTER
                    result["type"] = MediaType.MANGA
                elif inc2.group(1) in synonyms.terms["volume"]:
                    result["modifier"] = UpdateModifier.VOLUME
                    result["type"] = MediaType.MANGA
                else:
                    result["modifier"] = UpdateModifier.EPISODE

                result["term"] = inc2.group(2).strip(" '\"")

        # count updates

        cnt1 = re.search("(?:{}) (?:(?:the|my) )?(?:(episode|ep|chapter|chap|volume|vol)s? )?(?:count )?(?:(?:by|to) )?"
                         "(?:(\d+) )(?:(?:for|on) )(.+)".format(update_syns + "|" + increment_syns), query)
        cnt2 = re.search("(?:{}) (?:(?:the|my) )?(?:(episode|ep|chapter|chap|volume|vol)s? )?(?:count )?"
                         "(?:(?:of|for) )?(.+?) (?:(?:by|to) )?(?:(episode|ep|chapter|chap|volume|vol)s? )?(\d+)"
                         .format(update_syns + "|" + increment_syns), query)

        # if one of the rules matched
        if cnt1 or cnt2:
            result["operation"] = OperationType.UPDATE

            def assign_count_vals(modifier_group, term_group, value_group):
                """Assign the modifier, term and value of the match groups to result"""
                if modifier_group in synonyms.terms["chapter"]:
                    result["modifier"] = UpdateModifier.CHAPTER
                    result["type"] = MediaType.MANGA
                elif modifier_group in synonyms.terms["volume"]:
                    result["modifier"] = UpdateModifier.VOLUME
                    result["type"] = MediaType.MANGA
                else:
                    result["modifier"] = UpdateModifier.EPISODE

                result["term"] = term_group.strip(" '\"")
                result["value"] = int(value_group)

            if cnt1:
                assign_count_vals(cnt1.group(1), cnt1.group(3), cnt1.group(2))

            else:
                if cnt2.group(1) is not None:
                    assign_count_vals(cnt2.group(1), cnt2.group(2), cnt2.group(4))
                elif cnt2.group(3) is not None:
                    assign_count_vals(cnt2.group(3), cnt2.group(2), cnt2.group(4))

        # score updates

        # convert list of score syns to a string separated by | chars
        score_syns = "|".join(synonyms.terms["score"])

        scu1 = re.search("(?:{0}) (?:(?:the|my) )?(?:(?:{1}) )(?:(?:on|of) )?(?:the )?(?:({2}) )?(.+?) (?:({2}) )?"
                         "(?:(?:to|of) )?(-?\d\d?)".format(update_syns, score_syns, "anime|manga"), query)
        scu2 = re.search("(?:{0}) (?:(?:the|my) )?(?:({2}) )?(.+?) (?:({2}) )?(?:with )?(?:a )?(?:(?:{1}) )"
                         "(?:(?:to|of) )?(-?\d\d?)".format(update_syns, score_syns, "anime|manga"), query)

        # if one of the rules matched
        if scu1 or scu2:
            result["operation"] = OperationType.UPDATE
            result["modifier"] = UpdateModifier.SCORE

            def assign_score_vals(type_groups, term_group, value_group):
                if type_groups[0] == "manga" or type_groups[1] == "manga":
                    result["type"] = MediaType.MANGA
                else:
                    result["type"] = MediaType.ANIME

                result["term"] = term_group.strip(" '\"")
                result["value"] = int(value_group)

            if scu1:
                assign_score_vals((scu1.group(1), scu1.group(3)), scu1.group(2), scu1.group(4))

            else:
                assign_score_vals((scu2.group(1), scu2.group(3)), scu2.group(2), scu2.group(4))

        # status updates

        # convert list of status syns to a string separated by | chars
        status_syns = "|".join(synonyms.terms["status"])

        sts1 = re.search("(?:{0}) (?:(?:the|my) )?(?:({1}) )?(?:(?:on|of) )?(?:({2}) )?(.+?) (?:({2}) )?(?:with )?(?:a "
                         ")?(?:({1}) )?(?:(?:to|of|as) )?(?:(?:be|my) )?(watch(?:ing)?|read(?:ing)?|(?:on-?)? ?hold"
                         "|completed?|finish(?:ed)?|drop(?:ped)?|plan(?:ning)?(?: to (?:watch|read)?)?)"
                         .format(update_syns, status_syns, "anime|manga"), query)

        # if one of the rules matched
        if sts1:
            result["operation"] = OperationType.UPDATE
            result["modifier"] = UpdateModifier.STATUS
            result["term"] = sts1.group(3).strip(" '\"")

            if sts1.group(2) == "manga" or sts1.group(4) == "manga":
                result["type"] = MediaType.MANGA
            else:
                result["type"] = MediaType.ANIME

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
        # evaluate query using rules for view list requests

        result["operation"] = OperationType.VIEW_LIST

        # convert list of view list syns to a string separated by | chars
        viewlist_syns = "|".join(synonyms.actions["view_list"])

        vl1 = re.search("(?:{}) (?:me|us)?(?:my )?(?:(anime|manga) )?(?:list)".format(viewlist_syns), query)

        if vl1:
            if vl1.group(1) == "manga":
                result["type"] = MediaType.MANGA
        elif query.split()[-1] == "manga":
            result["type"] = MediaType.MANGA

    # return the filled out dictionary
    return result
