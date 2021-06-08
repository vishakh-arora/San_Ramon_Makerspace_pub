class Lockers:
    # example of DV attributes
    # attributes = [
    #     ['1000', '2000', '3000', '4000'], (building)
    #     ['1', '2'], (level)
    #     ['T', 'B'] (row)
    # ]
    def __init__(self, attributes):
        self.attributes = attributes

        def f(l, d_last):
            d = {}
            for i in l:
                d[i] = d_last
            return d.copy()

        d_last = {i:[] for i in attributes[-1]}
        for i in range(len(attributes)-2, -1, -1):
            d_last = f(attributes[i], d_last.copy())

        self.organized_lockers = d_last.copy()
        d_last = None
