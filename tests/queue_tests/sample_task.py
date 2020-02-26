import time


class SampleTask:
    def __init__(self):
        self.sequence = []
        time.sleep(10)

    def fibonacci(self, index):
        if index == 1:
            return 1
        elif index == 2:
            return 1
        else:
            return self.fibonacci(index - 2) + self.fibonacci(index - 1)

    def print_sequence(self):
        print(self.print_sequence())

    def get_sequence(self):
        return self.sequence
