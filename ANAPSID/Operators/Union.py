import abc

class _Union(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute(self, left, right, out):

        return

    @abc.abstractmethod
    def instantiate(self, d):

        return

    def getCardinality(self, l, r):
        c1 = l.getCardinality()
        c2 = r.getCardinality()
        return c1 + c2

    def getJoinCardinality(self, l, r, vars):
        return l.getJoinCardinality(vars) + r.getJoinCardinality(vars)

