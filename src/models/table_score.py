class TableScore(object):
    __score: int = 0  # naves que fueron disparados
    __goal: int = 50  # cuántas naves necesitan ser disparados para ganar
    __lost: int = 0  # naves erradas
    __max_lost: int = 5  # el jugador pierde si falla tantos disparos

    @property
    def score(self):
        return self.__score

    @score.setter
    def score(self, value):
        self.__score = value

    @property
    def lost(self):
        return self.__lost

    @lost.setter
    def lost(self, value):
        self.__lost = value

    @property
    def goal(self):
        return self.__goal

    @property
    def max_lost(self):
        return self.__max_lost
