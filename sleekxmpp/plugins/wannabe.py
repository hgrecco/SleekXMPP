import logging

__author__ = 'Hernan E. Grecco <hernan.grecco@gmail.com>'
__license__ = 'MIT License/X11 license'

class Wannabe(object):
    """An object that will become another."""

    def __init__(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs
        self.__calls = list()

    def __call__(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs

    def __getattr__(self, name):
        if name.startswith('_Wannabe__'):
            return super(Wannabe, self).__getattribute__(name.replace('_Wannabe', ''))
        else:
            h = Wannabe()
            self.__calls.append((name, h))
            return h

    def __setattr__(self, name, value):
        if name.startswith('_Wannabe__'):
            super(Wannabe, self).__setattr__(name.replace('_Wannabe', ''), value)
        else:
            self.__calls.append(('__setattr__', (name, value)))

    def __become(self, real_object):
        """Applies to real_object all calls applied to self."""
        for c, h in self.__calls:
            try:
                if c == '__setattr__':
                    setattr(real_object, h[0], h[1])
                    logging.debug('Executed pending call .%s = %r' % (h[0], h[1]))
                else:
                    getattr(real_object, c)(*h.__args, **h.__kwargs)
                    logging.debug('Executed pending call .%s(*args = %r, **kwargs = %r)' % (c, h.__args, h.__kwargs))
            except AttributeError as e:
                logging.debug(str(e))


if __name__ == '__main__':
    """This shows how the Wannabe object works."""
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')
    class test(object):

        def __init__(self, value):
            self.value = value
            self.other = 0

        def add(self, value):
            self.value = self.value + self.other + value

    obj = test(8)
    current = Wannabe()
    current.other = 10
    current.nothere()
    current.add(3)
    current._Wannabe__become(obj)
    del(current)
    print("The result is %d" % obj.value)
