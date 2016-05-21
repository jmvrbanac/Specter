from specter import util


class BaseForGetCalledSrcLine(object):

    def first(self, steps):
        return self.second(steps)


class SubclassForGetCalledSrcLine(BaseForGetCalledSrcLine):

    def second(self, steps):
        return util.get_called_src_line(steps=steps)
