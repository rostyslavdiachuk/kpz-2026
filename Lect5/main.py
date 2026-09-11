from dataclasses import dataclass
from functools import partial

a = [i for i in range(10) if i % 2 == 0]

l = []
for i in range(10):
    if i % 2 == 0:
        l.append(i)

result = l


def add(a, b):
    return a + b


# one_add = partial(add, a=1)
# print(one_add(2))

def curried_add(a:int):
    return lambda b: a + b

curried_add(2)
print(curried_add(2))


curried_add(3)
curried_add(5),(2)

for i in range(10):
    print(i)




from itertools import islice

def natural_numbers():
    n = 1
    while True:
        yield n
        n += 1

print(list(range(10)))



def doubled_evens(nums):
    for x in nums:
        d = x * 2
        if d % 2 == 0:
            yield d

pipeline = doubled_evens(natural_numbers())
print(list(islice(pipeline, 5)))
print(list(islice(pipeline, 5)))
print(list(islice(pipeline, 5)))


@dataclass(frozen=True)
class Num:
    value: float  # число


@dataclass(frozen=True)
class Neg:
    x: "Expr"  # унарний мінус


@dataclass(frozen=True)
class Add:
    a: "Expr"; b: "Expr"


@dataclass(frozen=True)
class Sub:
    a: "Expr"; b: "Expr"


@dataclass(frozen=True)
class Mul:
    a: "Expr"; b: "Expr"


@dataclass(frozen=True)
class Div:
    a: "Expr"; b: "Expr"


@dataclass(frozen=True)
class Pow:
    base: "Expr";
    exp: int  # exp — звичайне ціле, не піддерево


@dataclass(frozen=True)
class Sqrt: x: "Expr"  # квадратний корінь


@dataclass(frozen=True)
class Sum:
    terms: tuple["Expr", ...]  # сума довільної кількості виразів

Expr = Num | Neg | Add | Sub | Mul | Div | Pow | Sqrt | Sum
