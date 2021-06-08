import config
from copy import deepcopy

class Lockers:
    # example of DV attributes
    # attributes = [
    #     ['1000', '2000', '3000', '4000'], (building)
    #     ['1', '2'], (level)
    #     ['T', 'B'] (row)
    # ]

    # we can add lockers if spreadsheet columns are provided
    def __init__(self, spreadsheet, attributes):
        self.attributes = attributes
        self.s = spreadsheet

        def f(l, d_last):
          d = {}
          for i in l:
            d[i] = deepcopy(d_last)
          return d

        d_last = {i:list() for i in attributes[-1]}
        for i in range(len(attributes)-2, -1, -1):
            d_last = f(attributes[i], d_last)

        self.d = deepcopy(d_last)

    # adds a locker with given attributes
    def add_locker(self, attributes, locker_id):
        x = self.d
        for i in attributes:
            x = x[i]
        x.append(locker_id)

    # returns a locker based on attribute preference
    def get_locker(self, attributes):
        x = self.d
        for i in attributes:
            x = x[i]
        if len(x) != 0:
            return x.pop()
        return None
