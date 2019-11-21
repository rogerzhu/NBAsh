class Team:
    def __init__(self, name, score=0, player_list=None):
        self._player_list = player_list
        self._score = score
        self._name = name

    @property
    def players(self):
        return self._player_list

    @players.setter
    def players(self, value):
        self._player_list = value

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
