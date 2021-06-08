from copy import deepcopy

class Lockers:
    # example of DV attributes
    # attributes = [
    #     ['1000', '2000', '3000', '4000'], (building)
    #     ['1', '2'], (level)
    #     ['T', 'B'] (row)
    # ]
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
