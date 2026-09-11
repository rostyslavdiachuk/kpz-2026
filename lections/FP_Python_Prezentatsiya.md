---
theme: white
transition: slide
highlightTheme: atom-one-light
slideNumber: true
center: false
width: 1280
height: 720
margin: 0.08
font-family: JetBrains Mono
---
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

.reveal {
  --r-main-font: 'Inter', sans-serif;
  --r-heading-font: 'Inter', sans-serif;
  --r-code-font: 'JetBrains Mono', monospace;
}

.reveal pre code {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.55em;
}

.reveal h1, .reveal h2, .reveal h3 {
  font-weight: 700;
}
.reveal pre code { font-size: 1.35em !important; line-height: 1.45em !important; }
</style>
# Функціональна парадигма програмування в Python

Note: Вступні слова — перехід від ООП-мислення до функціонального стилю.

---

## Вступ
- Досі: об'єкти, класи, мутабельний стан
- Сьогодні: обчислення без побічних ефектів
- План: від математики до практичних інструментів Python

---

# 1. Математичний базис

---

## Лямбда-числення Алонзо Черча
- 1930-ті, паралельно з машиною Тюрінга <!-- .element: class="fragment" -->
- Обчислення = застосування функції до аргументу <!-- .element: class="fragment" -->
- Теза Черча–Тюрінга: еквівалентність машині Тюрінга <!-- .element: class="fragment" -->

--

### Нотація лямбда-числення
```
λx.x + 1          — визначення функції
(λx.x + 1) 5      — застосування, результат: 6
```

--

### У Python
```python
f = lambda x: x + 1
f(5)   # 6
```

---

## Чисті функції (Pure Functions)
- Детермінованість: той самий вхід → той самий вихід
- Відсутність побічних ефектів
- Тестованість, кешованість, безпечна паралелізація

--

```python
total = 0
def add_dirty(x):
    global total
    total += x
    return total

def add_pure(x, y):
    return x + y
```

Note: add_dirty залежить від зовнішнього стану, add_pure — самодостатня.

--

### Побічні ефекти — це
- Зміна глобальних змінних
- Мутація переданих аргументів
- I/O: файли, консоль, мережа, БД
- random(), поточний час

---

## Незмінність даних (Immutability)
- Незмінні типи: `int`, `str`, `tuple`, `frozenset`
- Змінні типи: `list`, `dict`, `set`
- Замість зміни — створення нового об'єкта

--

```python
point = (10, 20)
point[0] = 15   # TypeError

new_point = (point[0] + 5, point[1])
```

--

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

p1 = Point(10, 20)
p1.x = 15   # FrozenInstanceError
```

---

# 2. Механіка Python

---

## Функції першого класу (First-Class Citizens)
- Функції — об'єкти: присвоєння, аргумент, повернення
- Функції вищого порядку (Higher-Order Functions)

--

```python
funcs = [str.upper, str.lower, str.title]

def apply_twice(func, x):
    return func(func(x))

apply_twice(lambda x: x * 2, 5)   # 20
```

---

## Лямбда-вирази: обмеження
- Лише **один вираз**, не блок коду
- Заборонено: присвоєння, `for`, `while`, звичайний `if`-блок
- Дозволено: тернарний вираз

--

```python
classify = lambda x: "додатне" if x > 0 else "від'ємне"

sorted(students, key=lambda s: s.grade, reverse=True)
```

Note: PEP 8 радить не присвоювати lambda змінній — краще def.

---

## Замикання (Closures)
- Внутрішня функція "пам'ятає" оточення зовнішньої
- `nonlocal` для зміни захопленої змінної

--

```python
def make_multiplier(n):
    def multiplier(x):
        return x * n
    return multiplier

double = make_multiplier(2)
double(5)   # 10
```

--

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

counter = make_counter()
counter()   # 1
counter()   # 2
```

Note: Замикання — механізм, на якому побудовані partial і currying далі.

---

## Проміжний підсумок
- Черч → чисті функції → незмінність = **надійність**
- First-class functions → lambda → closures = **механіка Python**

Далі: конвеєри обробки даних 👉

---

# 3. Конвеєри та оптимізація пам'яті

---

## Map, Filter, Reduce
```python
from functools import reduce

data = [1, 2, 3, 4, 5, 6, 7, 8]

doubled = map(lambda x: x * 2, data)
evens   = filter(lambda x: x % 2 == 0, doubled)
total   = reduce(lambda a, b: a + b, evens, 0)   # 40
```

--

### Ідіоматичний варіант (list comprehension)
```python
total = sum(x * 2 for x in data if (x * 2) % 2 == 0)
```

Note: Гвідо хотів прибрати map/filter/reduce на користь comprehension; reduce переїхав у functools.

---

## Часткове застосування (Partial Application)
```python
from functools import partial

def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube   = partial(power, exponent=3)

square(5)   # 25
```

--

## Каррирування (Currying)
```python
def curry_add(x):
    def inner(y):
        return x + y
    return inner

add5 = curry_add(5)
add5(10)          # 15
curry_add(5)(10)  # 15
```

Note: partial фіксує аргументи багатоаргументної функції; currying перетворює її на ланцюжок одноаргументних.

---

## Рекурсія та стек викликів — база
- Рекурсія: функція викликає саму себе
- Кожен виклик створює новий **кадр стека** (stack frame)
- Кадр зберігає: локальні змінні + місце, куди повернутись
- Стек обмежений → занадто глибока рекурсія = переповнення

--

### Приклад: звичайна (НЕ хвостова) рекурсія
```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)   # множення ПІСЛЯ виклику!
```
Note: Кожен виклик мусить "почекати" результат вкладеного, щоб домножити на n — тому кадр не можна звільнити одразу.

--

### Що відбувається в стеку для factorial(4)
```
factorial(4)
  → factorial(3)
      → factorial(2)
          → factorial(1) = 1
          ← 1,  множимо на 2 → 2
      ← 2,  множимо на 3 → 6
  ← 6,  множимо на 4 → 24
```
- Усі 4 кадри одночасно "висять" у пам'яті — кожен чекає результат вкладеного виклику

---

## Хвостовий виклик (Tail Call) — що це
- Рекурсивний виклик — це **остання дія** у функції
- З результатом виклику більше нічого не робиться — він одразу повертається далі
- Отже, кадр поточного виклику вже нікому не потрібен

--

```python
def factorial_tail(n, acc=1):
    if n <= 1:
        return acc
    return factorial_tail(n - 1, n * acc)   # ніякого "множення після"
```
- `acc` накопичує результат заздалегідь, замість відкладеного множення при поверненні

--

### Ідея TCO (Tail Call Optimization)
- Якщо виклик хвостовий — можна **перевикористати** той самий кадр стека замість створення нового
- Рекурсія за пам'яттю стає схожою на цикл: стек не росте
- Підтримується у Scheme, Haskell, Scala (частково) — **але не в Python**

---

## Python свідомо не робить TCO
- Це не технічне обмеження — принципове рішення Гвідо ван Россума
- TCO "стирає" проміжні кадри → зникає повний traceback при помилці
- Філософія Python: "явне краще за неявне" — чесний стек важливіший за оптимізацію
- Наслідок: `RecursionError` після ~1000 викликів (`sys.getrecursionlimit()`)

---

## Симуляція без TCO
- Акумулятор (як `factorial_tail` вище) → змінює форму, але стек все одно росте в Python
- Явний цикл — найнадійніший спосіб

---

## Ліниві обчислення (Lazy Evaluation)
- `map`/`filter` уже ліниві за замовчуванням
- Генератори: `yield` та generator expression

--

```python
def lazy_pipeline(data):
    for x in data:
        d = x * 2
        if d % 2 == 0:
            yield d

pipeline = (x * 2 for x in data if (x * 2) % 2 == 0)
```

--

### Пам'ять: список vs генератор
```python
import sys

data = range(1_000_000)
sys.getsizeof([x * 2 for x in data])   # ~8 000 000 байт
sys.getsizeof((x * 2 for x in data))   # ~200 байт
```

---

## Практика: нескінченний потік
```python
from itertools import islice

def natural_numbers():
    n = 1
    while True:
        yield n
        n += 1

def doubled_evens(nums):
    for x in nums:
        d = x * 2
        if d % 2 == 0:
            yield d

pipeline = doubled_evens(natural_numbers())
list(islice(pipeline, 5))   # [2, 4, 6, 8, 10]
```

Note: зі списком замість генератора цей виклик ніколи б не завершився.

---

## Патерн-матчинг (Structural Pattern Matching)
- Python 3.10+, оператор `match` / `case` (PEP 634)
- У функціональних мовах (Haskell, Scala, OCaml) — стандартний спосіб розгалуження
- Найкраще розкривається саме з незмінними даними

--

### Базовий синтаксис
```python
def describe(value):
    match value:
        case 0:
            return "нуль"
        case n if n > 0:      # guard-умова
            return "додатне"
        case _:                # "інакше"
            return "від'ємне"
```

--

### Розбір структур (deconstruction)
```python
match point:
    case (0, 0):
        print("початок координат")
    case (x, 0):
        print(f"на осі X: {x}")
    case (x, y):
        print(f"точка ({x}, {y})")
```
- `case` не лише порівнює значення, а й **розпаковує** структуру одразу в змінні

--

### Матчинг класів
```python
@dataclass(frozen=True)
class Point:
    x: int
    y: int

match p:
    case Point(x=0, y=0):
        print("початок координат")
    case Point(x=x, y=y) if x == y:
        print("на діагоналі")
    case Point():
        print("звичайна точка")
```

--

### Чому це поруч із функціональним стилем
- Замінює довгі ланцюжки `if/elif` декларативною формою
- Природний партнер для `frozen dataclass` і `tuple` з попередніх лекцій
- В ФП-мовах pattern matching — головний спосіб працювати з алгебраїчними типами даних; у Python — його концептуальний родич, хоч і без повноцінних ADT

---

## Підсумок курсу
- Чисті функції + незмінність → **надійність**
- HOF + замикання → **композиційність**
- Map/filter/reduce + partial/curry → **техніка конвеєрів**
- Генератори → **масштабованість**
- Pattern matching → **декларативна робота з формою даних**

### Дякую за увагу!
