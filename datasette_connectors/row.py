class Row(list):
    def __init__(self, values=None):
        self.labels = []
        self.values = []
        if values:
            for idx in values:
                self.__setitem__(idx, values[idx])

    def __setitem__(self, idx, value):
        if type(idx) is str:
            if idx in self.labels:
                self.values[self.labels.index(idx)] = value
            else:
                self.labels.append(idx)
                self.values.append(value)
        else:
            self.values[idx] = value

    def __getitem__(self, idx):
        if type(idx) is str:
            return self.values[self.labels.index(idx)]
        else:
            return self.values[idx]

    def __iter__(self):
        return self.values.__iter__()
