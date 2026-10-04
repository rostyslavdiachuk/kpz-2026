from corrector.line import read, classify
from corrector.rules import rules, check

if __name__ == '__main__':
    with open('data/конспект.md') as file:
        lines = read(file.readlines());
        # print([classify(line) for line in lines])
        print(*check(lines))


expr = Add(Num(9),Add(Num(4), Num(5)))


def solve(expr):
    match (expr):
        case Num(a):
            return a
        case Add:
            return solve(expr.a) + solve(expr.b)
#4+5