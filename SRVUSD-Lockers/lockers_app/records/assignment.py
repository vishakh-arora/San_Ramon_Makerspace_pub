from copy import deepcopy
import itertools
from munkres import Munkres

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

class Match:
    def __init__(self, preferences):
        # initializing spreadsheet
        # self.s = spreadsheet
        # self.values = self.s.get_data()
        self.preferences = preferences
        # assuming first column is respondent and following three columns
        # are their preferences.
        self.x = {}
        for i in self.preferences:
            self.x[i[0]] = [j for j in i[1:] if j != '']
        # numerical ID for each person
        self.name2num = {i:j for i,j in zip([i[0] for i in self.preferences], range(len(self.x)))}
        self.num2name = {j:i for i,j in self.name2num.items()}

    # returns a list of length 2 lists of IDs
    def get_partners(self):
        # initialization
        for i in self.name2num.keys():
          for j in range(len(self.x[i])):
            self.x[i][j] = self.name2num[self.x[i][j]]
          self.x[self.name2num[i]] = self.x.pop(i)

        m = [[0 for i in range(len(self.x))] for i in range(len(self.x))]
        for i in self.x.keys():
          for j in self.x.keys():
            cost = 0
            if j in self.x[i]:
              cost += self.x[i].index(j)
            else:
              cost += 10
            if i in self.x[j]:
              cost += self.x[j].index(i)
            else:
              cost += 10
            if i == j:
              cost += 10
            m[i][j] = cost

        # # DEBUG
        # print('MATRIX:')
        # print(*m, sep='\n')
        # print()

        # running munkres algorithm
        o = Munkres()
        idxs = o.compute(m)
        ans = []

        # listing partnerships
        cost = 0
        partnered = [False for i in range(len(self.x))]

        for a, b in idxs:
          # # DEBUG
          # print(a, b, self.num2name[a], self.num2name[b], 'COST: ', m[a][b])
          cost += m[a][b]
          # neither person has been partnered
          if [b, a] not in ans and not partnered[a] and not partnered[b]:
              partnered[a] = True
              partnered[b] = True
              ans.append([self.num2name[a], self.num2name[b]])
              continue

        # # DEBUG
        # print('TOTAL COST: ', cost//2)
        return ans
