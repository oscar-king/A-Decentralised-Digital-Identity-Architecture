import json

from charm.core.math.integer import integer


class SigConversion:
    @classmethod
    def modint2strlist(cls, elem) -> list:
        """
        Converts an integer or a modular integer into JSON list. If the integer does not have a modulus it will return
        a singleton list. The number at index 0 is the integer and the number at index 1 is the modulus.
        :param elem: modular integer
        :return: JSON list
        """
        ls = str(elem).split(" mod ")
        return json.dumps(ls)

    @classmethod
    def strlist2modint(cls, ls: str) -> integer:
        """
        Takes a JSON list and converts it into a modular integer or integer depending on the list's length.
        :param ls: JSON list
        :return: integer
        """
        ls = json.loads(ls)
        if len(ls) == 2:
            return integer(int(ls[0])) % integer(int(ls[1]))
        elif len(ls) == 1:
            return integer(int(ls[0]))
        else:
            raise Exception

    @classmethod
    def convert_dict_strlist(cls, dictionary: dict) -> dict:
        """
        Convert a dictionary of modular integers (or integers) to a dictionary of List<str>.
        :param dictionary: (dict)
        :return: dictionary (dict) of List<str>. Each value takes the form [integer, modulus]
        """
        for x in dictionary:
            dictionary[x] = SigConversion.modint2strlist(dictionary[x])
        return dictionary

    @classmethod
    def convert_dict_modint(cls, dictionary: dict) -> dict:
        """
            Convert a dictionary of Lists of strings to a dictionary of integers
            :param dictionary: (dict)
            :return: dictionary (dict) of integer. Each value takes the form [integer, modulus]
        """
        for x in dictionary:
            dictionary[x] = SigConversion.strlist2modint(dictionary[x])
        return dictionary
