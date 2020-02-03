from framework.interfaces.persistence.persistor import Persistor
from framework.interfaces.persistence.restorer import Restorer


class Persistence(Persistor, Restorer):
    def __init__(self):
        pass

    def persist(self):
        pass

    def restore(self):
        pass
