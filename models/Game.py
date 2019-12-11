class Game:
    def __init__(self, index, team_a, team_b, time):
        self._team_a = team_a
        self._team_b = team_b
        self._time = time
        self._index = index

    @property
    def teamA(self):
        return self._team_a

    @teamA.setter
    def teamA(self, value):
        self._team_a = value

    @property
    def teamB(self):
        return self._team_b

    @teamB.setter
    def teamB(self, value):
        self._team_b = value

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value
