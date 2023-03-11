class PlayerAction:
    def __init__(self, action):
        self.action = action

    def __str__(self): return self.action

    def __cmp__(self, other):
        return cmp(self.action, other.action)

    def __hash__(self):
        return hash(self.action)
