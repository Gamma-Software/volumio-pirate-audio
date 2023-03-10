# StateMachine/StateMachine.py
# Takes a list of Inputs to move from State to
# State using a template method.

class PlayerStateMachine:
    def __init__(self, initialState):
        self.currentState = initialState
        self.volume = 50  # by default the volume is 50%
        self.currentState.run()

