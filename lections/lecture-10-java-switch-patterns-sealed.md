---
theme: white
highlightTheme: atom-one-light
transition: slide
width: 1280
height: 800
margin: 0.06
---

# Сучасний контроль потоку виконання

### Switch Expressions, Pattern Matching та Sealed-ієрархії в Java

note: Лекція лише про Java. Працюємо на Java 27 (GA 15.09.2026). Усе, крім примітивних патернів, — стабільні фічі, які є вже в LTS 21/25. Примітивні патерни в 27 — п'ятий preview, показую окремим слайдом.

---

## План

1. Еволюція `switch`: від інструкції до виразу <!-- element class="fragment" -->
2. Pattern Matching для `instanceof` <!-- element class="fragment" -->
3. Pattern Matching у `switch`: типи, `null`, guard-умови <!-- element class="fragment" -->
4. Record patterns — деконструкція об'єктів <!-- element class="fragment" -->
5. Sealed-класи та інтерфейси, `permits` <!-- element class="fragment" -->
6. Алгебраїчні типи даних і перевірка вичерпності <!-- element class="fragment" -->
7. Практика <!-- element class="fragment" -->

---

## Хронологія фіч

| Версія | Що з'явилось | JEP |
|---|---|---|
| Java 7 | `switch` по `String` | — |
| **Java 14** | Switch expressions, `->`, `yield` | 361 |
| **Java 16** | Pattern matching для `instanceof`, Records | 394, 395 |
| **Java 17** | Sealed classes / interfaces | 409 |
| **Java 21** | Pattern matching для `switch`, Record patterns | 441, 440 |
| Java 22 | Безіменні змінні та шаблони `_` | 456 |
| **Java 25** (LTS) | Компактні файли, `void main()`, `IO.println` | 512 |
| **Java 27** | Примітивні типи в шаблонах — *5-й preview* | 532 |

note: 17, 21, 25 — LTS. Повний набір для data-oriented programming стабільний з 21-ї. Примітивні патерни в preview з Java 23 (JEP 455 → 488 → 507 → 530 → 532), у 27-й — без змін відносно 26-ї.

---

# Частина 1
## Еволюція `switch`

---

## Класичний switch statement

```java
int day = 3;
String name;

switch (day) {
    case 1:
        name = "Понеділок";
        break;
    case 2:
        name = "Вівторок";
        break;
    case 3:
        name = "Середа";
        // забули break...
    case 4:
        name = "Четвер";
        break;
    default:
        name = "Невідомо";
}
System.out.println(name); // Четвер 🤡
```

note: Питання до аудиторії: що виведе? Fall-through — класичне джерело багів, яке успадковано з C.

---

## Проблеми старого `switch`

- **Fall-through** за замовчуванням — забутий `break` = баг <!-- element class="fragment" -->
- Це **інструкція**, а не вираз — не повертає значення <!-- element class="fragment" -->
- Змінну доводиться оголошувати *до* switch і присвоювати в кожній гілці <!-- element class="fragment" -->
- Одна область видимості на всі `case` — конфлікти імен змінних <!-- element class="fragment" -->
- Компілятор не перевіряє, чи всі варіанти покрито <!-- element class="fragment" -->
- Працює лише з `int`-подібними типами, `enum`, `String` <!-- element class="fragment" -->

---

## Стрілкові мітки `->` (Java 14)

```java
switch (day) {
    case 1, 2, 3, 4, 5 -> System.out.println("Робочий день");
    case 6, 7          -> System.out.println("Вихідний");
    default            -> System.out.println("Такого дня немає");
}
```

- Немає fall-through — виконується **лише одна** гілка <!-- element class="fragment" -->
- Кілька значень через кому в одному `case` <!-- element class="fragment" -->
- Кожна гілка — окремий блок зі своєю областю видимості <!-- element class="fragment" -->

---

## Switch **expression** — повертає значення

```java
String name = switch (day) {
    case 1 -> "Понеділок";
    case 2 -> "Вівторок";
    case 3 -> "Середа";
    case 4 -> "Четвер";
    case 5 -> "П'ятниця";
    case 6, 7 -> "Вихідний";
    default -> throw new IllegalArgumentException("День: " + day);
};
```

- `switch` стоїть праворуч від `=` — це **вираз** <!-- element class="fragment" -->
- Змінну можна зробити `final` / `var` <!-- element class="fragment" -->
- Вираз **зобов'язаний** бути вичерпним — інакше помилка компіляції <!-- element class="fragment" -->
- Гілка може кинути виняток замість значення <!-- element class="fragment" -->

---

## `yield` — коли потрібен блок коду

```java
int bonus = switch (level) {
    case JUNIOR -> 100;
    case MIDDLE -> 300;
    case SENIOR -> {
        int base = 500;
        int extra = yearsInCompany * 50;
        yield base + extra;   // "повернути" значення з гілки
    }
};
```

> `return` тут не підходить — він вийшов би з **методу**, а не зі `switch`.

note: yield — контекстне ключове слово, не зарезервоване. Змінну з ім'ям yield оголосити можна, але не варто.

---

## `yield` у старому синтаксисі

```java
int code = switch (status) {
    case "OK":
        yield 200;
    case "NOT_FOUND":
        yield 404;
    default:
        yield 500;
};
```

- Switch expression можна писати і з `:` <!-- element class="fragment" -->
- Але тоді повертається fall-through → на практиці завжди використовуйте `->` <!-- element class="fragment" -->
- Змішувати `:` і `->` в одному switch **не можна** <!-- element class="fragment" -->

---

## Вичерпність для `enum`

```java
enum TrafficLight { RED, YELLOW, GREEN }

String action = switch (light) {
    case RED    -> "Стоп";
    case YELLOW -> "Увага";
    case GREEN  -> "Рух";
    // default не потрібен — усі константи покрито
};
```

Додали `FLASHING` в enum → **код не скомпілюється**, поки не обробите новий варіант.

<!-- element class="fragment" -->
Саме тому **не пишіть `default`** там, де можна його уникнути — він "ковтає" нові варіанти мовчки.

note: Це перша зустріч із ідеєю exhaustiveness. Повернемось до неї в кінці лекції, вже на sealed-типах.

---

# Частина 2
## Pattern Matching для `instanceof`

---

## Як було: перевірка + приведення

```java
Object obj = getValue();

if (obj instanceof String) {
    String s = (String) obj;        // повторюємо тип
    System.out.println(s.length());
} else if (obj instanceof Integer) {
    Integer i = (Integer) obj;      // і ще раз
    System.out.println(i + 1);
}
```

Тричі пишемо той самий тип: перевірка, оголошення, приведення.

---

## Як стало (Java 16)

```java
if (obj instanceof String s) {
    System.out.println(s.length());
} else if (obj instanceof Integer i) {
    System.out.println(i + 1);
}
```

- `String s` — **type pattern**: перевірка + приведення + зв'язування змінної <!-- element class="fragment" -->
- `s` — pattern variable, доступна лише там, де збіг **гарантовано** <!-- element class="fragment" -->

---

## Flow scoping — де видно змінну

```java
// 1. У поєднанні з &&
if (obj instanceof String s && s.length() > 5) {
    System.out.println(s.toUpperCase());
}

// 2. Через заперечення + ранній вихід
if (!(obj instanceof String s)) {
    return;
}
System.out.println(s.length()); // s тут видна!

// 3. А так — ні
if (obj instanceof String s || s.isEmpty()) { } // ❌ помилка компіляції
```

note: Компілятор аналізує потік виконання: змінна в області видимості там, де збіг точно відбувся. Для || збіг не гарантований.

---

## Класичний приклад: `equals`

```java
public final class Point {
    private final int x, y;

    @Override
    public boolean equals(Object o) {
        return o instanceof Point other
            && x == other.x
            && y == other.y;
    }
}
```

Замість 6–8 рядків — один вираз.

---

# Частина 3
## Pattern Matching у `switch` (Java 21)

---

## Switch по типах

```java
static String describe(Object obj) {
    return switch (obj) {
        case Integer i -> "Ціле число: " + i;
        case Long l    -> "Довге число: " + l;
        case String s  -> "Рядок довжини " + s.length();
        case int[] arr -> "Масив з " + arr.length + " елементів";
        default        -> "Щось інше: " + obj;
    };
}
```

- Тепер `switch` приймає **будь-який** посилальний тип <!-- element class="fragment" -->
- `case` містить **шаблон**, а не константу <!-- element class="fragment" -->
- Для `Object` потрібен `default` — інакше не вичерпно <!-- element class="fragment" -->

---

## `null` у switch

```java
// Старий switch на null → NullPointerException
switch (str) { case "a" -> ...; } // NPE, якщо str == null

// Java 21: null можна обробити явно
String result = switch (obj) {
    case null      -> "Порожньо";
    case String s  -> "Рядок: " + s;
    default        -> "Інше";
};

// Або об'єднати з default
switch (obj) {
    case String s -> handle(s);
    case null, default -> fallback();
}
```

> Без `case null` поведінка лишилась старою: NPE.

---

## Guard-умови: `when`

```java
static String classify(Object obj) {
    return switch (obj) {
        case Integer i when i < 0  -> "Від'ємне";
        case Integer i when i == 0 -> "Нуль";
        case Integer i             -> "Додатне";
        case String s when s.isBlank() -> "Порожній рядок";
        case String s              -> "Рядок: " + s;
        default                    -> "Невідомо";
    };
}
```

- `when` — додаткова булева умова до шаблону <!-- element class="fragment" -->
- Гілки перевіряються **зверху вниз** <!-- element class="fragment" -->
- Guarded-гілки не рахуються для вичерпності — потрібна "страхувальна" гілка без `when` <!-- element class="fragment" -->

---

## Домінування шаблонів

```java
switch (obj) {
    case CharSequence cs -> "Послідовність символів";
    case String s        -> "Рядок";   // ❌ помилка компіляції
    default              -> "Інше";
}
```

`String` — підтип `CharSequence`, тому друга гілка **ніколи** не спрацює.

<!-- element class="fragment" -->
Правило: **від конкретного до загального**. Компілятор перевіряє це сам.

```java
switch (obj) {
    case String s        -> "Рядок";          // ✅
    case CharSequence cs -> "Інша послідовність";
    default              -> "Інше";
}
```
<!-- element class="fragment" -->

---

# Частина 4
## Record Patterns — деконструкція

---

## Нагадування: records

```java
record Point(int x, int y) {}
```

Компілятор генерує:
- `private final` поля `x`, `y` <!-- element class="fragment" -->
- канонічний конструктор <!-- element class="fragment" -->
- аксесори `x()`, `y()` <!-- element class="fragment" -->
- `equals`, `hashCode`, `toString` <!-- element class="fragment" -->

<!-- element class="fragment" -->
Record — **прозорий носій даних**: ми точно знаємо його компоненти, тому можемо його "розібрати".

---

## Record pattern (Java 21)

```java
Object obj = new Point(3, 4);

// Type pattern — отримуємо об'єкт
if (obj instanceof Point p) {
    System.out.println(p.x() + p.y());
}

// Record pattern — одразу отримуємо компоненти
if (obj instanceof Point(int x, int y)) {
    System.out.println(x + y);
}
```

Деконструкція = перевірка типу + виклик аксесорів + зв'язування змінних.

---

## Вкладена деконструкція

```java
enum Color { RED, GREEN, BLUE }
record Point(int x, int y) {}
record ColoredPoint(Point p, Color color) {}
record Rectangle(ColoredPoint upperLeft, ColoredPoint lowerRight) {}

static void printUpperLeft(Object obj) {
    if (obj instanceof Rectangle(
            ColoredPoint(Point(var x, var y), var color),
            var lowerRight)) {
        System.out.println("(" + x + ", " + y + ") колір " + color);
    }
}
```

- Шаблони можна вкладати на довільну глибину <!-- element class="fragment" -->
- `var` — компілятор виведе тип компонента сам <!-- element class="fragment" -->
- Без жодного `getUpperLeft().getP().getX()` <!-- element class="fragment" -->

---

## Record patterns у switch

```java
record Pair<A, B>(A first, B second) {}

static String describe(Pair<Object, Object> pair) {
    return switch (pair) {
        case Pair(String a, String b)   -> "Два рядки: " + a + b;
        case Pair(Integer a, Integer b) -> "Сума: " + (a + b);
        case Pair(var a, var b) when a == null || b == null
                                        -> "Є null";
        case Pair(var a, var b)         -> "Змішана пара";
    };
}
```

Останній `case Pair(var a, var b)` покриває всі випадки → `default` не потрібен.

note: Generic-параметри в шаблоні вивести можна: Pair(var a, var b) замість Pair<Object,Object>(Object a, Object b).

---

## Безіменні шаблони `_`

```java
// Було (Java 21) — змушені давати ім'я непотрібній змінній
case ColoredPoint(Point(var x, var y), var ignored) -> ...

// Зараз
case ColoredPoint(Point(var x, _), _) -> "x = " + x;
case Circle _ -> "Якесь коло";          // тип важливий, змінна — ні
```

- `_` — "мені байдуже, що там" <!-- element class="fragment" -->
- Робить намір явним і прибирає warning про невикористану змінну <!-- element class="fragment" -->
- Також працює в `catch (Exception _)`, лямбдах `(_, v) -> v`, `for` <!-- element class="fragment" -->

---

## Примітивні типи в шаблонах (preview)

```java
// Java 27: javac/java --enable-preview --release 27
String status = switch (httpCode) {            // int
    case 200 -> "OK";
    case int c when c >= 400 && c < 500 -> "Помилка клієнта: " + c;
    case int c when c >= 500            -> "Помилка сервера: " + c;
    case int c                          -> "Інше: " + c;
};

String answer = switch (flag) {                // boolean!
    case true  -> "Так";
    case false -> "Ні";
};
```

- `switch` працює з **усіма** примітивами: `long`, `float`, `double`, `boolean` <!-- element class="fragment" -->
- Константи й type patterns можна змішувати <!-- element class="fragment" -->

---

## `instanceof` як безпечне приведення

```java
double d = 42.0;
if (d instanceof int i) {        // збіг, лише якщо конвертація без втрат
    IO.println("Ціле: " + i);   // 42
}

long big = 5_000_000_000L;
if (big instanceof int i) { }    // false — не влізе в int

int x = 300;
switch (x) {
    case byte b -> IO.println("Влазить у byte: " + b);
    case int i  -> IO.println("Лише int: " + i);
}
```

<!-- element class="fragment" -->
> `instanceof` тепер перевіряє не лише **тип**, а й **чи не втратимо значення**.
> Замість ручних перевірок діапазонів `if (x >= -128 && x <= 127)`.

note: Це все ще preview — у продакшені не використовуємо, але напрям розвитку мови показовий: патерни стають однаковими для примітивів і посилальних типів. Всередині record patterns примітиви (int x) працюють стабільно ще з 21-ї.

---

# Частина 5
## Sealed-класи та інтерфейси

---

## Проблема: відкриті ієрархії

```java
public abstract class Shape { }

public class Circle extends Shape { }
public class Square extends Shape { }

// ...де завгодно, хто завгодно:
public class Banana extends Shape { } // 🍌
```

- `final` — забороняє успадкування **повністю** <!-- element class="fragment" -->
- Без модифікатора — дозволяє **будь-кому** <!-- element class="fragment" -->
- А якщо потрібно "лише ці три підтипи і більше ніхто"? <!-- element class="fragment" -->

---

## `sealed` + `permits` (Java 17)

```java
public sealed class Shape permits Circle, Square, Rectangle { }

public final class Circle extends Shape {
    final double radius;
    Circle(double radius) { this.radius = radius; }
}

public final class Square extends Shape {
    final double side;
    Square(double side) { this.side = side; }
}

public non-sealed class Rectangle extends Shape {
    final double w, h;
    Rectangle(double w, double h) { this.w = w; this.h = h; }
}
```

`Shape` сам визначає, **хто** може його розширювати.

---

## Правила для підкласів

Кожен дозволений підклас **зобов'язаний** обрати один модифікатор:

| Модифікатор | Значення |
|---|---|
| `final` | Далі успадковувати не можна |
| `sealed` | Продовжує закриту ієрархію, має свій `permits` |
| `non-sealed` | "Відкриває" гілку — далі може успадковувати будь-хто |

<!-- element class="fragment" -->
Record-и неявно `final`, тому ідеально підходять як листки ієрархії.

note: non-sealed — перше ключове слово Java з дефісом. Це свідомий "вихід" з обмеження, і його видно в коді.

---

## Додаткові обмеження

- Підкласи мають **напряму** розширювати sealed-тип <!-- element class="fragment" -->
- Мають бути в тому ж **модулі** (або в тому ж **пакеті**, якщо модулів немає) <!-- element class="fragment" -->
- Якщо всі підкласи в тому ж файлі — `permits` можна **опустити**, компілятор виведе список сам <!-- element class="fragment" -->

```java
public sealed interface Vehicle {
    record Car(String model) implements Vehicle {}
    record Bike(int gears) implements Vehicle {}
    record Truck(double loadTons) implements Vehicle {}
}
```
<!-- element class="fragment" -->

---

## Sealed interface + records + enum

```java
public sealed interface Shape permits Circle, Square, Triangle, Unit {}

public record Circle(double r) implements Shape {}
public record Square(double side) implements Shape {}
public record Triangle(double a, double b, double c) implements Shape {}

public enum Unit implements Shape { POINT, EMPTY }
```

- Інтерфейс — найчастіший вибір для кореня ієрархії <!-- element class="fragment" -->
- `enum` теж може бути дозволеним підтипом (він неявно `final`/`sealed`) <!-- element class="fragment" -->

---

## Рефлексія

```java
Class<?> c = Shape.class;

c.isSealed();                // true
c.getPermittedSubclasses();  // [Circle, Square, Triangle, Unit]
```

Інформація про закритість зберігається в байткоді (атрибут `PermittedSubclasses`) і перевіряється **JVM** під час завантаження класів, а не лише компілятором.

---

# Частина 6
## Алгебраїчні типи даних

---

## Тип як множина значень

Тип — це **множина** можливих значень. Рахуємо її розмір `|T|`:

| Тип                               | Можливі значення       | N(T) |     |
| --------------------------------- | ---------------------- | ---- | --- |
| `boolean`                         | `true`, `false`        | 2    |     |
| `enum Color { RED, GREEN, BLUE }` | `RED`, `GREEN`, `BLUE` | 3    |     |
| `enum Unit { INSTANCE }`          | `INSTANCE`             | 1    |     |
| `byte`                            | від −128 до 127        | 256  |     |

<!-- element class="fragment" -->
**Алгебраїчний тип даних** — тип, зібраний з інших за допомогою двох операцій: **добутку** та **суми**.

note: Слово "алгебраїчні" буквальне: кількість значень складеного типу рахується звичайною арифметикою. Це не абстракція заради абстракції — на цьому рахунку тримається ідея "неможливі стани не мають бути виразимими".

---

## Тип-добуток (product type)

"Значення має **і** A, **і** B"

```java
record Pixel(boolean visible, Color color) {}
```

| visible | color |
|---|---|
| true | RED / GREEN / BLUE |
| false | RED / GREEN / BLUE |

`|Pixel| = |boolean| × |Color| = 2 × 3 = 6`
<!-- element class="fragment" -->

- У Java добуток — це `record` (або будь-який клас з полями) <!-- element class="fragment" -->
- Кортеж, структура, запис — усе це добутки <!-- element class="fragment" -->

---

## Тип-сума (sum type)

"Значення є **або** A, **або** B — рівно одним із варіантів"

```java
sealed interface Light {
    record Off() implements Light {}              // 1
    record On(Color color) implements Light {}    // 3
    record Blinking(Color color, boolean fast) implements Light {} // 3 × 2
}
```

`|Light| = 1 + 3 + 6 = 10`
<!-- element class="fragment" -->

- У Java сума — це `sealed`-ієрархія <!-- element class="fragment" -->
- "Тег" варіанта — **клас** об'єкта; його перевіряє pattern matching <!-- element class="fragment" -->
- Інші назви: tagged union, discriminated union, variant, coproduct <!-- element class="fragment" -->

note: Без sealed ієрархія інтерфейсу — це "сума з невідомою кількістю доданків", компілятор не може нічого порахувати, отже й перевірити вичерпність.

---

## `enum` vs `sealed`

```java
enum Suit { HEARTS, DIAMONDS, CLUBS, SPADES }        // 1 + 1 + 1 + 1
```

```java
sealed interface Card {
    record Pip(Suit suit, int rank) implements Card {}     // 4 × 9 (2–10)
    record Face(Suit suit, char kind) implements Card {}   // 4 × 3 (J, Q, K)
    record Joker() implements Card {}                      // 1
}
```

| | `enum` | `sealed` + `record` |
|---|---|---|
| Варіанти | фіксовані **об'єкти** | фіксовані **типи** |
| Дані у варіанті | однакові поля для всіх | **свої** поля в кожного |
| Екземплярів варіанта | рівно один | скільки завгодно |

<!-- element class="fragment" -->
`enum` — окремий випадок суми, де кожен варіант має рівно одне значення.

---

## Алгебра працює буквально

| Алгебра | Java |
|---|---|
| `0` | тип без значень (у Java прямого аналога немає) |
| `1` | `record Unit()` / `enum { INSTANCE }` |
| `A × B` | `record Pair<A, B>(A a, B b)` |
| `A + B` | `sealed` з двома варіантами |
| `T + 1` | `Optional<T>` — або значення, або нічого |
| `T + E` | `Result<T>` — або значення, або помилка |

<!-- element class="fragment" -->
Дистрибутивність: `A × (B + C) = A × B + A × C`

```java
record Order(String id, Delivery d) {}          // id × (Courier + Pickup)
// ≅
sealed interface Order2 {                        // id × Courier + id × Pickup
    record CourierOrder(String id, String address) implements Order2 {}
    record PickupOrder(String id, int pointNo) implements Order2 {}
}
```
<!-- element class="fragment" -->

note: Обидві моделі містять ту саму інформацію — це і є ізоморфізм. Яку обрати — питання зручності: де частіше потрібен спільний id.

---

## Неможливі стани — невиразні

❌ Класичний "мішок полів":

```java
class Connection {
    Status status;       // DISCONNECTED, CONNECTING, CONNECTED, FAILED
    String sessionId;    // лише коли CONNECTED
    String error;        // лише коли FAILED
    int attempt;         // лише коли CONNECTING
}
```

- `CONNECTED` без `sessionId`? `FAILED` з `sessionId`? Тип це **дозволяє** <!-- element class="fragment" -->
- Кожен метод мусить перевіряти "а чи узгоджені поля" <!-- element class="fragment" -->
- Кількість станів: `4 × |String| × |String| × |int|` — майже всі **некоректні** <!-- element class="fragment" -->

---

## Неможливі стани — невиразні

✅ Сума добутків:

```java
sealed interface Connection {
    record Disconnected()               implements Connection {}
    record Connecting(int attempt)      implements Connection {}
    record Connected(String sessionId)  implements Connection {}
    record Failed(String error)         implements Connection {}
}
```

`1 + |int| + |String| + |String|` — **кожне** значення коректне.
<!-- element class="fragment" -->

```java
String info(Connection c) {
    return switch (c) {
        case Disconnected()   -> "Офлайн";
        case Connecting(var n) -> "Спроба №" + n;
        case Connected(var id) -> "Сесія " + id;   // id точно є
        case Failed(var err)   -> "Помилка: " + err;
    };
}
```
<!-- element class="fragment" -->

note: Формулювання Ярона Мінскі: make illegal states unrepresentable. Перевірку інваріантів ми переносимо з runtime у систему типів.

---

## Рекурсивні ADT

Тип може посилатися сам на себе:

```java
sealed interface MyList<T> {
    record Nil<T>() implements MyList<T> {}
    record Cons<T>(T head, MyList<T> tail) implements MyList<T> {}
}

sealed interface Tree {
    record Leaf(int value) implements Tree {}
    record Node(Tree left, Tree right) implements Tree {}
}
```

```java
int sum(Tree t) {
    return switch (t) {
        case Leaf(var v)       -> v;
        case Node(var l, var r) -> sum(l) + sum(r);
    };
}
```

- Структура типу **підказує** структуру функції: один `case` на варіант, рекурсія на рекурсивне поле <!-- element class="fragment" -->
- `Expr` з інтерпретатора (далі) — теж рекурсивний ADT <!-- element class="fragment" -->

---

## Звідки це прийшло

```haskell
-- Haskell
data Shape = Circle Double | Square Double
```

```rust
// Rust
enum Shape { Circle(f64), Square(f64) }
```

```java
// Java 21+
sealed interface Shape {
    record Circle(double r) implements Shape {}
    record Square(double side) implements Shape {}
}
```

<!-- element class="fragment" -->
Java прийшла до ADT з боку ООП: сума — це закрита ієрархія класів, добуток — клас-носій даних. Синтаксис довший, але ідея та сама, і компілятор гарантує те саме.


---

## Синергія: вичерпний switch без `default`

```java
sealed interface Shape permits Circle, Square, Triangle {}
record Circle(double r) implements Shape {}
record Square(double side) implements Shape {}
record Triangle(double base, double height) implements Shape {}

static double area(Shape shape) {
    return switch (shape) {
        case Circle(var r)          -> Math.PI * r * r;
        case Square(var s)          -> s * s;
        case Triangle(var b, var h) -> 0.5 * b * h;
    };
}
```

Компілятор **знає всі** підтипи `Shape` → може перевірити, що кожен оброблено.

---

## Додаємо новий підтип

```java
sealed interface Shape permits Circle, Square, Triangle, Hexagon {}
record Hexagon(double side) implements Shape {}
```

```text
error: the switch expression does not cover all possible input values
        return switch (shape) {
               ^
```
<!-- element class="fragment" -->

- Компілятор покаже **кожне** місце, де забули обробити `Hexagon` <!-- element class="fragment" -->
- З `default` цього б не сталося — баг дожив би до продакшену <!-- element class="fragment" -->

note: Це головна ідея лекції. Помилку, яка раніше була runtime-багом, ми перенесли на етап компіляції. Якщо ж новий підклас з'явиться через роздільну компіляцію — JVM кине MatchException, а не мовчки піде в невідому гілку.

---

## Вичерпність з вкладеними шаблонами

```java
sealed interface Opt<T> permits Some, None {}
record Some<T>(T value) implements Opt<T> {}
record None<T>() implements Opt<T> {}

record Pair<A, B>(A a, B b) {}

static <T> String both(Pair<Opt<T>, Opt<T>> p) {
    return switch (p) {
        case Pair(Some(var x), Some(var y)) -> "Обидва: " + x + ", " + y;
        case Pair(Some(var x), None())      -> "Лише перший: " + x;
        case Pair(None(), Some(var y))      -> "Лише другий: " + y;
        case Pair(None(), None())           -> "Нічого";
    };
}
```

Компілятор перевіряє всі **комбінації** 2 × 2.

---

## Приклад: інтерпретатор виразів

```java
sealed interface Expr {
    record Num(int value)            implements Expr {}
    record Add(Expr left, Expr right) implements Expr {}
    record Mul(Expr left, Expr right) implements Expr {}
    record Neg(Expr inner)            implements Expr {}
}

static int eval(Expr e) {
    return switch (e) {
        case Num(var v)        -> v;
        case Add(var l, var r) -> eval(l) + eval(r);
        case Mul(var l, var r) -> eval(l) * eval(r);
        case Neg(var inner)    -> -eval(inner);
    };
}

// (2 + 3) * -4
Expr expr = new Mul(new Add(new Num(2), new Num(3)), new Neg(new Num(4)));
eval(expr); // -20
```

note: Класичне дерево абстрактного синтаксису. Код читається майже як математичне означення.

---

## Pattern Matching vs Visitor

| | Visitor (класичне ООП) | Sealed + switch |
|---|---|---|
| Нова **операція** | Новий клас-Visitor | Новий метод зі switch ✅ |
| Новий **тип** | Змінювати всі Visitor-и | Змінювати всі switch-і |
| Бойлерплейт | `accept`, `visit` × N | Мінімальний ✅ |
| Вичерпність | Через інтерфейс Visitor | Компілятор ✅ |

<!-- element class="fragment" -->
**Expression problem**: ООП-поліморфізм зручний, коли часто додаються *типи*; ADT + pattern matching — коли часто додаються *операції*.

---

## Коли що використовувати

**Віртуальний метод у класі**, якщо:
- поведінка — невід'ємна частина об'єкта <!-- element class="fragment" -->
- ієрархія відкрита для розширення (плагіни, фреймворки) <!-- element class="fragment" -->

**Sealed + pattern matching**, якщо:
- набір варіантів **відомий і скінченний** (стани, події, команди, результати) <!-- element class="fragment" -->
- операції над даними живуть окремо від даних <!-- element class="fragment" -->
- важливо, щоб компілятор ловив необроблені випадки <!-- element class="fragment" -->

note: Брайан Гетц називає цей підхід data-oriented programming: моделюємо дані як незмінні прозорі значення, а логіку пишемо як функції над ними.

---

## Підсумок

- `switch` став **виразом**: `->`, без fall-through, `yield`, вичерпність <!-- element class="fragment" -->
- `instanceof` і `switch` працюють із **шаблонами** типів <!-- element class="fragment" -->
- `when` — умови, `case null` — явна обробка null <!-- element class="fragment" -->
- **Record patterns** розбирають об'єкт на компоненти, навіть вкладені <!-- element class="fragment" -->
- **Sealed**-типи фіксують скінченний набір підтипів <!-- element class="fragment" -->
- Разом: **ADT + вичерпність на етапі компіляції** <!-- element class="fragment" -->
- Далі — примітивні патерни: один механізм для **всіх** типів <!-- element class="fragment" -->

---

# Практика

---

## Як запускати задачі

Один файл, без класу-обгортки й без `public static` (Java 25+):

```java
// Shapes.java
sealed interface Shape {
    record Circle(double r) implements Shape {}
    record Square(double side) implements Shape {}
}

double area(Shape s) {
    return switch (s) {
        case Shape.Circle(var r)  -> Math.PI * r * r;
        case Shape.Square(var a)  -> a * a;
    };
}

void main() {
    IO.println(area(new Shape.Circle(1)));
}
```

```bash
java Shapes.java                                   # без компіляції
java --enable-preview --source 27 Shapes.java      # для preview-фіч
```

note: Компактний файл автоматично імпортує java.base, тож List, Map, Optional доступні без import. Зручно для live-coding на парі. Увага: у компактному файлі вкладені записи доводиться кваліфікувати (Shape.Circle), бо імпортувати з безіменного пакета не можна. На слайдах із розв'язками імена скорочено — або кваліфікуйте, або оголошуйте записи на верхньому рівні файлу.

---

## Задача 1. Рефакторинг

Перепишіть у сучасному стилі (switch expression, без `default`, якщо можливо):

```java
enum Month { JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC }

int days;
switch (month) {
    case FEB:
        days = isLeap ? 29 : 28;
        break;
    case APR: case JUN: case SEP: case NOV:
        days = 30;
        break;
    default:
        days = 31;
}
```

Додатково: чому `default` тут поганий вибір?

--

## Задача 1. Розв'язок

```java
int days = switch (month) {
    case FEB -> isLeap ? 29 : 28;
    case APR, JUN, SEP, NOV -> 30;
    case JAN, MAR, MAY, JUL, AUG, OCT, DEC -> 31;
};
```

`default` сховав би помилку, якби хтось додав у enum неіснуючий місяць (або, реалістичніше, новий стан в іншому enum).

---

## Задача 2. Комісія платежів

Змоделюйте платіжні методи як sealed-ієрархію:

- `Card(String number, boolean international)` — 1.5 %, для міжнародних — 3 %
- `PayPal(String email)` — 2.9 % + 0.30
- `Crypto(String coin)` — `BTC` 1 %, решта — 0.5 %
- `Cash()` — без комісії

Напишіть `double fee(Payment p, double amount)` одним switch-виразом **без `default`**.

Потім додайте `ApplePay` — і подивіться, що скаже компілятор.

--

## Задача 2. Розв'язок

```java
sealed interface Payment {
    record Card(String number, boolean international) implements Payment {}
    record PayPal(String email) implements Payment {}
    record Crypto(String coin) implements Payment {}
    record Cash() implements Payment {}
}

static double fee(Payment p, double amount) {
    return switch (p) {
        case Card(_, var intl) when intl -> amount * 0.03;
        case Card _                      -> amount * 0.015;
        case PayPal _                    -> amount * 0.029 + 0.30;
        case Crypto(var coin) when coin.equals("BTC") -> amount * 0.01;
        case Crypto _                    -> amount * 0.005;
        case Cash()                      -> 0;
    };
}
```

> У реальному коді для грошей — `BigDecimal`, не `double`.

---

## Задача 3. Спрощення виразів

Для `Expr` з лекції напишіть `Expr simplify(Expr e)`:

- `x + 0` → `x`, `0 + x` → `x`
- `x * 1` → `x`, `x * 0` → `0`, `0 * x` → `0`
- `-(-x)` → `x`
- `Num(a) + Num(b)` → `Num(a + b)`
- інакше — рекурсивно спростити піддерева

Також напишіть `String show(Expr e)`, що виводить вираз з дужками.

--

## Задача 3. Розв'язок

```java
static Expr simplify(Expr e) {
    return switch (e) {
        case Add(Num(var a), Num(var b))        -> new Num(a + b);
        case Add(var l, Num(var z)) when z == 0 -> simplify(l);
        case Add(Num(var z), var r) when z == 0 -> simplify(r);
        case Mul(var l, Num(var o)) when o == 1 -> simplify(l);
        case Mul(var l, Num(var z)) when z == 0 -> new Num(0);
        case Mul(Num(var z), var r) when z == 0 -> new Num(0);
        case Neg(Neg(var inner))                -> simplify(inner);
        case Add(var l, var r) -> new Add(simplify(l), simplify(r));
        case Mul(var l, var r) -> new Mul(simplify(l), simplify(r));
        case Neg(var inner)    -> new Neg(simplify(inner));
        case Num n             -> n;
    };
}
```

note: Зверніть увагу: guarded-гілки йдуть перед загальними, а вичерпність забезпечують останні чотири. Питання для обговорення: чи досягне simplify нерухомої точки за один прохід? (Ні — (0+0)*5 треба спрощувати двічі.)

---

## Задача 4. Result замість винятків

Реалізуйте тип:

```java
sealed interface Result<T> {
    record Ok<T>(T value) implements Result<T> {}
    record Err<T>(String message) implements Result<T> {}
}
```

1. `Result<Integer> parseInt(String s)`
2. `Result<Integer> divide(int a, int b)` — помилка при `b == 0`
3. Обробіть рядки `"10"`, `"abc"`, `"0"` так: розпарсити, поділити 100 на число, вивести результат або помилку — через switch

--

## Задача 4. Розв'язок

```java
static Result<Integer> parseInt(String s) {
    try {
        return new Ok<>(Integer.parseInt(s));
    } catch (NumberFormatException ex) {
        return new Err<>("Не число: " + s);
    }
}

static Result<Integer> divide(int a, int b) {
    return b == 0 ? new Err<>("Ділення на нуль") : new Ok<>(a / b);
}

for (String input : List.of("10", "abc", "0")) {
    Result<Integer> r = switch (parseInt(input)) {
        case Ok(var n)  -> divide(100, n);
        case Err(var m) -> new Err<>(m);
    };
    String msg = switch (r) {
        case Ok(var v)  -> "Результат: " + v;
        case Err(var m) -> "Помилка: " + m;
    };
    IO.println(msg);
}
```

---

## Задача 5. Скінченний автомат замовлення

Стани (sealed):
`New`, `Paid(double amount)`, `Shipped(String trackingNo)`, `Delivered`, `Cancelled(String reason)`

Події (sealed):
`Pay(double amount)`, `Ship(String trackingNo)`, `Deliver`, `Cancel(String reason)`

Напишіть `OrderState next(OrderState s, OrderEvent e)`.

**Підказка:** зробіть `record Transition(OrderState s, OrderEvent e)` і switch по ньому:

```java
return switch (new Transition(state, event)) {
    case Transition(New n, Pay(var amount)) -> new Paid(amount);
    // ...
    case Transition(var s, var e) ->
        throw new IllegalStateException(s + " + " + e);
};
```

Питання: скасувати можна до відправлення — як це виразити одним `case`?

---

## Задача 6. JSON (для охочих)

```java
sealed interface Json {
    record JNull() implements Json {}
    record JBool(boolean value) implements Json {}
    record JNumber(double value) implements Json {}
    record JString(String value) implements Json {}
    record JArray(List<Json> items) implements Json {}
    record JObject(Map<String, Json> fields) implements Json {}
}
```

1. `String stringify(Json j)` — серіалізація в рядок
2. `int depth(Json j)` — максимальна глибина вкладеності
3. `Optional<Json> get(Json j, String... path)` — доступ за шляхом, напр. `get(doc, "user", "address", "city")`

Жодного `instanceof` і жодного `default`!

---

## Задача 7. Примітивні патерни (preview)

Запуск: `java --enable-preview --source 27 Grades.java`

1. `String grade(int score)` — шкала ECTS (A: 90–100, B: 82–89, …, F: 0–34) через `case int s when ...`; значення поза 0–100 — виняток
2. `String fits(long value)` — у який найменший тип влазить число: `byte`, `short`, `int` чи лише `long`
3. `String describe(double d)` — "ціле" (якщо `d instanceof int`), "дробове", "NaN" чи "нескінченність"

Питання: чому у п. 2 порядок `case` важливий і що скаже компілятор, якщо поставити `case int` перед `case short`?

---

## Задача 8. Рахуємо стани

```java
class Task {
    boolean done;
    boolean cancelled;
    LocalDate deadline;      // може бути null
    LocalDate completedAt;   // має бути лише якщо done
    String cancelReason;     // має бути лише якщо cancelled
}
```

1. Назвіть 3 комбінації полів, які клас дозволяє, але які не мають сенсу
2. Перепишіть `Task` як суму добутків (`sealed` + `record`), щоб ці комбінації стали **невиразними**
3. Напишіть `String status(Task t)` через switch без `default`
4. Опційний `deadline` — зробіть його окремим ADT `Deadline = None | At(LocalDate)` і порівняйте з `Optional<LocalDate>`

--

## Задача 8. Розв'язок

```java
sealed interface Deadline {
    record None() implements Deadline {}
    record At(LocalDate date) implements Deadline {}
}

sealed interface Task {
    record Open(String title, Deadline deadline) implements Task {}
    record Done(String title, LocalDate completedAt) implements Task {}
    record Cancelled(String title, String reason) implements Task {}
}

String status(Task t) {
    return switch (t) {
        case Open(var title, Deadline.None())    -> title + ": без терміну";
        case Open(var title, Deadline.At(var d)) -> title + ": до " + d;
        case Done(var title, var when)           -> title + ": виконано " + when;
        case Cancelled(var title, var why)       -> title + ": скасовано (" + why + ")";
    };
}
```

note: Неможливі стани оригіналу: done && cancelled; done без completedAt; cancelReason без cancelled; completedAt без done. Зверніть увагу, що вичерпність перевіряється і для вкладеного Deadline.

---

# Питання?

