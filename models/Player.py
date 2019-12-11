class Player:
    def __init__(self, stat_dict={}):
        self._stat_dict = stat_dict

    @property
    def stat_dict(self):
        return self.stat_dict

    @stat_dict.setter
    def stat_dict(self, value):
        self._stat_dict = value
