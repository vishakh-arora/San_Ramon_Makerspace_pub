from copy import deepcopy
import itertools

class Lockers:
    # example of DV attributes
    # attributes = [
    #     ['1000', '2000', '3000', '4000'], (building)
    #     ['1', '2'], (level)
    #     ['T', 'B'] (row)
    # ]
    # example of DV priority
    # priority = [
    #     ['1', 'T'],
    #     ['2', 'T'],
    #     ['1', 'B'],
    #     ['2', 'B']
    # ]


    # we can add lockers if spreadsheet columns are provided
    def __init__(self, attributes):
        self.attributes = attributes

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
    def add_locker(self, attributes, locker_ids):
        x = self.d
        for i in attributes:
            x = x[i]
        for i in locker_ids:
            x.append(i)

    # returns a locker based on attribute preference
    def get_locker(self, attributes):
        x = self.d
        for i in attributes:
            x = x[i]
        if len(x) != 0:
            return x.pop()
        else:
            return None
