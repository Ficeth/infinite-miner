class Cutscene:
    def __init__(self, game):
        self.game = game

        self.timer = 0
        self.action_count = -1

        self.action_started = False

        self.finished = False

    def actions(self):
        return True

    def update(self):
        if self.finished:
            return True

        self.action_started = False

        self.timer -= 1
        if self.timer <= 0:
            self.action_started = True
            self.action_count += 1

        self.finished = self.actions()

        return False