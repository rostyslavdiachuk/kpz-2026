# def add(a,b):
#     return a+b
# def sub(a,b):
#     return a-b
#
#
class Foo:
    pass
class Bar:
    def add(self, a, b):
        return a + b
#
# a = Foo()
# b = Foo()
# a.name = "Hello"
#
# print(a.name)
# print(b.name)
def plus(a, b):
    return a+b

a = Foo()

a = {}
{add: plus}


# superAdd = add
# add(1,2)
# superAdd(1,2)
a.add = plus
# b = Bar()
# b.add(1,2)
print(a.add(1,2))


def applyAdd(a):
    print(a)
    return a.plus(1, 2)


a = 10

f = Foo()
print(a)
def doMagic():
    global f
    f = 10101

doMagic()
print(f)

print (a)

from math import sin


def a ():
    import math
    pass
