---
theme: white
highlightTheme: atom-one-light
transition: slide
width: 1280
height: 800
margin: 0.06
slideNumber: c/t
---

<!-- slide bg="#1F4E79" -->

<style>
.reveal h1, .reveal h2, .reveal h3 { color: #1F4E79; text-transform: none; }
.reveal h1 { font-size: 1.9em; }
.reveal h2 { font-size: 1.45em; }
.reveal pre { width: 100%; font-size: 0.5em; box-shadow: none; }
.reveal pre code { max-height: 620px; }
.reveal table { font-size: 0.6em; }
.reveal li, .reveal p { font-size: 0.85em; }
.reveal .muted { color: #777; font-size: 0.7em; }
.reveal .warn { border-left: 8px solid #9B2C2C; background: #F9E3E3; padding: 10px 20px; text-align: left; }
.reveal .note { border-left: 8px solid #1F4E79; background: #DCE8F4; padding: 10px 20px; text-align: left; }
.reveal .tip { border-left: 8px solid #2E6B3A; background: #E6F2E8; padding: 10px 20px; text-align: left; }
</style>

<span style="color:#DCE8F4">Лекція 7</span>

# <span style="color:white">Основи Java та управління пам'яттю</span>

## <span style="color:#DCE8F4">Вступ до ООП</span>

<span style="color:#DCE8F4; font-size:0.7em">JVM · типи даних · стек і купа · GC · класи · інкапсуляція</span>

---

## План

1. Архітектура JVM і точка входу
2. Статична типізація, примітиви vs посилання, стек vs купа
3. Введення-виведення, умови, цикли, масиви
4. Збирання сміття
5. Анатомія класу
6. Абстрагування та інкапсуляція

note: Наприкінці — типові помилки та контрольні запитання.

---

# 1. Архітектура JVM

---

## Проблема переносимості

<split even gap="3">

<div>

**C / C++**

+ компіляція в машинний код
+ окрема збірка під кожну ОС і процесор
+ Windows x64 ≠ Linux ARM

</div>

<div>

**Java**

+ компіляція в **байт-код**
+ байт-код однаковий скрізь
+ платформо-залежна лише **JVM**

</div>

</split>

<div class="note fragment">

**Write Once, Run Anywhere** — один `.class` виконується на будь-якій сумісній JVM

</div>

---

## Від коду до виконання

![[jvm_arch.png]] <!-- element style="width:78%" -->

note: Пройтися згори донизу: javac → .class → Class Loader → Runtime Data Areas → Execution Engine. Показати, що все, про що говоримо далі в лекції, живе в зелених блоках.

---

## JDK, JRE, JVM

| Компонент | Що містить | Кому |
|---|---|---|
| **JVM** | завантажувач класів, пам'ять, виконавчий рушій, GC | «двигун» |
| **JRE** | JVM + стандартна бібліотека | користувачу |
| **JDK** | JRE + `javac`, `jshell`, `javap`, `jar`, `jcmd`, `jlink` | розробнику |

<div class="note fragment">

З Java 11 окремий JRE не постачається — ставимо **JDK**, а мінімальний runtime збираємо через `jlink`

</div>

---

## Class Loader Subsystem

+ **Loading** — пошук і читання `.class`
	+ Bootstrap → Platform → Application
+ **Linking**
	+ *verify* — перевірка байт-коду
	+ *prepare* — пам'ять під static-поля
	+ *resolve* — символьні посилання → реальні
+ **Initialization** — `static`-блоки та static-поля

<p class="muted fragment">Класи завантажуються ліниво — при першому зверненні. Делегування батькові не дає підмінити <code>java.lang.String</code>.</p>

---

## Runtime Data Areas

| Область | Що зберігає | Доступ |
|---|---|---|
| **Heap** | усі об'єкти та масиви | спільна |
| **Metaspace** | метадані класів, байт-код методів | спільна |
| **JVM Stack** | кадри викликів: локальні змінні, операнди | на потік |

note: Metaspace з Java 8 замінила PermGen і живе в нативній пам'яті, а не в купі.

---

## Execution Engine

<split even gap="3">

<div>

**Інтерпретатор**

+ стартує миттєво
+ виконує повільно

</div>

<div>

**JIT-компілятор**

+ стежить за «гарячим» кодом
+ C1 — швидко, C2 — агресивно оптимізує
+ дає «розігрів» програми

</div>

</split>

<div class="note fragment">

Java — **керована мова**: перевірка типів, меж масивів і звільнення пам'яті — на боці runtime

</div>

---

## Точка входу

```java [1-2|3-4]
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, JVM!");
        System.out.println("Аргументів: " + args.length);
    }
}
```

| `public` | `static` | `void` | `main` | `String[] args` |
|---|---|---|---|---|
| JVM викликає ззовні | об'єктів ще немає | код виходу — `System.exit()` | фіксоване ім'я | аргументи CLI |

---

## Компіляція і запуск

```bash
$ javac Main.java            # -> Main.class
$ java Main alpha beta       # args = ["alpha", "beta"]
$ java Main.java             # без явної компіляції (Java 11+)
$ javap -c Main              # подивитися байт-код
```

```text
0: getstatic     #7  // Field java/lang/System.out
3: ldc           #13 // String Hello, JVM!
5: invokevirtual #15 // Method java/io/PrintStream.println
8: return
```
<!-- element class="fragment" -->

note: Демо: скомпілювати й показати javap -c. Номери в пулі констант можуть відрізнятися.

---

# 2. Типи даних і пам'ять

---

## Статична типізація

| | Статична (Java, C++, Kotlin) | Динамічна (Python, JS) |
|---|---|---|
| Перевірка типів | під час компіляції | під час виконання |
| Помилка типу | не скомпілюється | виняток у рантаймі |
| Підказки IDE | точні | евристичні |

```java
var name = "Java";   // тип String
name = "Kotlin";     // OK
name = 42;           // помилка компіляції
```
<!-- element class="fragment" -->

<p class="muted fragment"><code>var</code> — виведення типу, а не динамічна типізація</p>

---

## 8 примітивних типів

| Тип | Розмір | Діапазон | За замовч. |
|---|---|---|---|
| `byte` | 1 байт | −128 … 127 | `0` |
| `short` | 2 байти | −32 768 … 32 767 | `0` |
| `int` | 4 байти | ≈ ±2,1 млрд | `0` |
| `long` | 8 байтів | ≈ ±9,2·10¹⁸, суфікс `L` | `0L` |
| `float` | 4 байти | 6–7 цифр, суфікс `f` | `0.0f` |
| `double` | 8 байтів | 15–16 цифр | `0.0` |
| `char` | 2 байти | UTF-16, 0 … 65 535 | `'\u0000'` |
| `boolean` | не визначено | `true` / `false` | `false` |

---

## Пастки з примітивами

<div class="warn">

Значення за замовчуванням мають лише **поля** та **елементи масивів**.
Локальна змінна без ініціалізації → *помилка компіляції*

</div>

<div class="warn fragment">

`0.1 + 0.2` → `0.30000000000000004`
Для грошей — `BigDecimal`

</div>

---

## Приведення типів

```java [1-2|4-5|7-8|10-11]
int i = 100;
long l = i;                  // розширення — неявно

double pi = 3.99;
int t = (int) pi;            // звуження — явно → 3

byte b = (byte) 300;         // → 44
int max = Integer.MAX_VALUE;

System.out.println(max + 1); // -2147483648, без помилки!
Math.addExact(max, 1);       // ArithmeticException
```

note: Переповнення цілих у Java мовчазне. Якщо критично — Math.*Exact.

---

## Примітиви vs посилання

| | Примітивні | Посилальні |
|---|---|---|
| Змінна зберігає | значення | посилання на об'єкт |
| Де дані | у кадрі стеку (локальні) | об'єкт — у купі |
| `null` | неможливий | можливий |
| `a = b` | копія значення | копія посилання |
| `==` | порівнює значення | чи це **той самий** об'єкт |
| Дженерики | `List<int>` ✘ | `List<Integer>` ✔ |

Посилальні: класи, інтерфейси, масиви, `enum`, `record`

---

## Стек і купа
<split even gap="2"> 

<div>

**Стек** 

+ окремий для кожного потоку 
+ кадр на кожен виклик методу 
+ звільняється миттєво 
+ обмежений (`-Xss`) 
+ `StackOverflowError` 

</div> 

<div> 

**Купа** 

+ спільна для всіх потоків 
+ тут усі об'єкти (`new`) 
+ звільняє GC 
+ розмір `-Xms` / `-Xmx` 
+ `OutOfMemoryError` 

</div> 


</split>

---

## Що де лежить

```java [3-4|5|6|7-9|10-12]
public class MemoryDemo {
    public static void main(String[] args) {
        int count = 3;               // значення в кадрі main
        double price = 99.5;
        Point p = new Point(1, 2);   // p — у стеку, об'єкт — у купі
        int[] data = {10, 20, 30};   // масив — завжди об'єкт
        Point q = p;                 // копія посилання
        q.x = 100;
        System.out.println(p.x);     // 100
        int copy = count;            // копія значення
        copy++;
        System.out.println(count);   // 3
    }
}
```

---

## Картина пам'яті

![[stack_heap.png]] <!-- element style="width:82%" -->

---

## Точніше кажучи…

+ **локальні змінні** (і примітиви, і посилання) — у кадрі стеку
+ **поля об'єкта**, навіть `int`, — всередині об'єкта, тобто в купі
+ **статичні поля** — разом з об'єктом класу, теж у купі
+ JIT може через **escape analysis** не створювати об'єкт у купі взагалі

<p class="muted fragment">«Примітиви в стеку, об'єкти в купі» — корисне, але спрощення</p>

---

## Параметри завжди передаються за значенням

```java [1|3|5-7|10-12|14-15|17-18]
static void increment(int n) { n++; }

static void moveRight(Point p) { p.x += 10; }

static void replace(Point p) {
    p = new Point(0, 0);         // лише локальна копія
}

public static void main(String[] args) {
    int a = 5;
    increment(a);
    System.out.println(a);       // 5

    Point pt = new Point(1, 1);
    moveRight(pt);               // pt.x == 11

    replace(pt);
    System.out.println(pt.x);    // 11, а не 0
}
```

note: Для об'єктів копіюється значення посилання. Через нього можна змінити об'єкт, але не можна перенаправити змінну викликача.

---

## Обгортки та автопакування

`int` ↔ `Integer`, `double` ↔ `Double`, `char` ↔ `Character` …

```java [1-3|5-6|8-10|12-13]
Integer a = 127, b = 127;
Integer c = 128, d = 128;
System.out.println(a == b);       // true  — кеш −128..127

System.out.println(c == d);       // false — різні об'єкти
System.out.println(c.equals(d));  // true

String s1 = "java", s2 = "java";
String s3 = new String("java");
System.out.println(s1 == s2);     // true  — String pool

System.out.println(s1 == s3);     // false
Integer n = null; int x = n;      // NullPointerException
```

<div class="warn fragment">

Об'єкти порівнюємо через `equals()`, а не `==`

</div>

---

# 3. Введення-виведення, умови, цикли, масиви

---

## Виведення

```java
System.out.print("Без переходу. ");
System.out.println("З переходом.");
System.out.printf("Студентка %s, бал %.2f%n", name, avg);
String r = "%s / %d курс".formatted(name, 2);   // Java 15+
System.err.println("Помилка");
```

| `%d` | `%.2f` | `%s` | `%c` | `%b` | `%n` |
|---|---|---|---|---|---|
| ціле | дробове | рядок | символ | boolean | новий рядок |

---

## Введення: `Scanner`

```java [4-5|6|7-8|9-10]
import java.util.Scanner;

public class InputDemo {
    public static void main(String[] args) {
        try (Scanner in = new Scanner(System.in)) {
            System.out.print("Вік: ");
            int age = in.nextInt();
            in.nextLine();               // «з'їдаємо» залишок рядка
            System.out.print("Ім'я: ");
            String name = in.nextLine();
            System.out.printf("Привіт, %s! Вам буде %d%n", name, age + 5);
        }
    }
}
```

<p class="muted fragment">Великі обсяги даних — <code>BufferedReader</code>. Кирилиця у Windows-консолі — <code>chcp 65001</code> або <code>-Dstdout.encoding=UTF-8</code></p>

---

## Умови: класика

```java
if (score >= 90) return "A";
else if (score >= 75) return "B";
else return "F";

String parity = (n % 2 == 0) ? "парне" : "непарне";
```

<div class="warn fragment">

Класичний `switch` без `break` «провалюється» в наступну гілку

</div>

---

## Switch-вирази (Java 14+)

```java
String type = switch (day) {
    case "SAT", "SUN" -> "вихідний";
    case "MON", "TUE", "WED", "THU", "FRI" -> "робочий";
    default -> throw new IllegalArgumentException(day);
};
```

+ повертає значення
+ без fall-through
+ перевірка повноти для `enum` і `sealed`

---

## Цикли

| Цикл | Коли |
|---|---|
| `for (init; cond; step)` | відома кількість / потрібен індекс |
| `for (T x : items)` | перебір усіх елементів |
| `while (cond)` | кількість невідома |
| `do { } while (cond)` | хоча б один раз |

```java
outer:
for (int r = 0; r < 3; r++)
    for (int c = 0; c < 3; c++)
        if (r * c == 2) break outer;   // вихід з обох циклів
```
<!-- element class="fragment" -->

---

## Масиви — це об'єкти

```java [1-2|4-5|7-10|12-13]
int[] a = new int[5];            // [0, 0, 0, 0, 0]
String[] names = new String[3];  // [null, null, null]

int[] b = {5, 3, 9, 1};
Arrays.sort(b);                  // [1, 3, 5, 9]

int[] alias = b;                 // те саме посилання!
int[] copy = Arrays.copyOf(b, b.length);
alias[0] = 42;                   // b[0] == 42, copy[0] == 1
System.out.println(Arrays.equals(b, copy));

int[][] jagged = new int[3][];   // «рвучкий» масив
jagged[0] = new int[1]; jagged[1] = new int[2];
```

---

## Масиви: що запам'ятати

+ розмір фіксований (динамічний — `ArrayList`)
+ довжина — поле `length`, без дужок
+ індекс від 0, вихід за межі → `ArrayIndexOutOfBoundsException`
+ `String[]` зберігає **посилання**, спочатку `null`
+ `==` порівнює посилання, вміст — `Arrays.equals`
+ утиліти: `toString`, `deepToString`, `sort`, `copyOf`, `fill`

---

# 4. Збирання сміття

---

## Навіщо GC

<split even gap="3">

<div>

**Ручне керування (C/C++)**

+ `malloc` / `free`, `new` / `delete`
+ витоки пам'яті
+ висячі покажчики
+ подвійне звільнення

</div>

<div>

**Java**

+ оператора `delete` немає
+ пам'ять звільняє **збирач сміття**
+ цілий клас помилок зникає

</div>

</split>

---

## Досяжність

Об'єкт живий, якщо до нього є шлях від **коренів GC**:

+ локальні змінні в стеках потоків
+ статичні поля
+ активні потоки
+ JNI-посилання

<div class="note fragment">

Не підрахунок посилань → **циклічні** структури, недосяжні ззовні, теж збираються

</div>

---

## Цикл — не завада

```java [1-4|7-9|11-13|15]
static class Node {
    Node next;
    byte[] payload = new byte[1024 * 1024];
}

public static void main(String[] args) {
    Node a = new Node();
    Node b = new Node();
    a.next = b; b.next = a;      // цикл посилань

    a = null;
    b = null;                    // обидва недосяжні
                                 // → будуть зібрані

    System.gc();                 // лише ПІДКАЗКА для JVM
}
```

---

## Базові алгоритми

| Алгоритм | Суть | Ціна |
|---|---|---|
| **Mark-Sweep** | позначити живих, звільнити решту | фрагментація |
| **Mark-Compact** | + зсунути живих упритул | час на переміщення |
| **Copying** | скопіювати живих в іншу область | удвічі більше місця |

<div class="warn fragment">

**Stop-The-World** — паузи, коли потоки застосунку стоять. Мета сучасних GC — мінімізувати їх

</div>

---

## Шлях об'єкта

1. `new` → **Eden**
2. Eden заповнений → **Minor GC**, живі → **Survivor**
3. Кожен Minor GC: S0 ⇄ S1, вік +1
4. Вік ≥ порогу → **promotion** в **Old Generation**
5. Old заповнений → **Major / Full GC** (дорого)

---

## Збирачі в HotSpot

| Збирач | Прапорець | Для чого |
|---|---|---|
| Serial | `-XX:+UseSerialGC` | малі купи, одне ядро |
| Parallel | `-XX:+UseParallelGC` | максимальна пропускна здатність |
| **G1** | `-XX:+UseG1GC` | **за замовчуванням з Java 9**, баланс |
| ZGC | `-XX:+UseZGC` | паузи < 1 мс на величезних купах |
| Shenandoah | `-XX:+UseShenandoahGC` | низькі паузи |

---

## Спостерігаємо за GC

```bash
java -Xms256m -Xmx1g -XX:+UseG1GC -Xlog:gc Main

jcmd <pid> GC.heap_info       # стан купи
jstat -gcutil <pid> 1000      # статистика щосекунди
```

<div class="tip">

Живий графік пам'яті — **VisualVM** або **JDK Mission Control**

</div>

note: Демо: запустити GcDemo з -Xlog:gc, показати тип паузи та скільки звільнено.

---

## `finalize()` — чому ні

+ немає гарантії, **коли** і **чи** буде викликаний
+ об'єкт живе щонайменше на один цикл GC довше
+ може «воскресити» об'єкт
+ винятки мовчки ігноруються

<div class="warn fragment">

Deprecated з Java 9, **for removal** з Java 18 (JEP 421)

</div>

---

## Витоки пам'яті в Java — реальні

+ статичні колекції, куди лише додають
+ слухачі подій, які не відписують
+ незакриті потоки та з'єднання
+ `ThreadLocal` у пулах потоків

Для кешів: `SoftReference` · `WeakReference` (`WeakHashMap`) · `PhantomReference`
<!-- element class="fragment" -->

---

# 5. Анатомія класу

---

## Клас і об'єкт

<split even gap="3">

**Клас** — креслення

**Об'єкт** — конкретний екземпляр у купі

</split>

| Елемент | Призначення |
|---|---|
| Поля | стан |
| Конструктори | коректний початковий стан |
| Методи | поведінка |
| Блоки ініціалізації | `static { }`, `{ }` |
| Вкладені типи | класи, записи, переліки |

---

## Поля

```java
private static int createdCount = 0;     // одне на клас
public static final int MAX_GRADE = 100; // константа

private final int id;                    // присвоюється один раз
private String name;                     // поле екземпляра
private final List<Integer> grades;
```

<div class="warn fragment">

`final` фіксує **посилання**, а не об'єкт: `grades.add(…)` усе ще працює

</div>

---

## Методи

+ **сигнатура** = ім'я + типи параметрів
+ **перевантаження** — однакове ім'я, різні параметри
+ методи екземпляра мають `this`
+ `static`-методи — ні: `Student.getCreatedCount()`

```java
public void addGrade(int grade) { ... }
public void addGrade(int... many) { ... }   // перевантаження

this.name = name;   // поле vs параметр
```

---

## Модифікатори доступу

| | Клас | Пакет | Підкласи | Усі |
|---|:-:|:-:|:-:|:-:|
| `private` | ✔ | ✘ | ✘ | ✘ |
| *package-private* | ✔ | ✔ | ✘ | ✘ |
| `protected` | ✔ | ✔ | ✔ | ✘ |
| `public` | ✔ | ✔ | ✔ | ✔ |

<div class="tip fragment">

Починайте з `private` і відкривайте лише за реальної потреби

</div>

---

## Конструктор за замовчуванням

```java [1-4|6-11]
class Point {
    int x, y;
}
Point a = new Point();       // OK — компілятор згенерував Point() {}

class Vector {
    double dx, dy;
    Vector(double dx, double dy) { ... }
}

Vector v = new Vector();     // помилка компіляції!
```

<p class="muted fragment">Генерується лише тоді, коли інших конструкторів немає</p>

---

## Параметри та ланцюжок

```java [1-3|5-10]
public Student() {
    this("Невідомий", 1);        // делегуємо іншому конструктору
}

public Student(String name, int course) {
    this.id = ++createdCount;
    this.name = name;
    setCourse(course);           // перевірка через метод
    this.grades = new ArrayList<>();
}
```

---

## Конструктор копіювання

```java
public Student(Student other) {
    this.id = ++createdCount;                      // новий id
    this.name = other.name;                        // String незмінний
    this.course = other.course;
    this.grades = new ArrayList<>(other.grades);   // глибока копія
}
```

---

## Порядок ініціалізації

```java
public class InitOrder {
    static { System.out.println("1. static-блок"); }
    private int value = log("2. ініціалізатор поля");
    { System.out.println("3. блок екземпляра"); }
    public InitOrder() { System.out.println("4. конструктор"); }
}
```

<div class="note fragment">

`static`-блок — **один раз** при першому використанні класу; 2–4 — для кожного `new`

</div>

---

# 6. Абстрагування та інкапсуляція

---

## Абстрагування

> Виділяємо суттєве, відкидаємо несуттєве для задачі

| Рівень | Бачимо | Приховано |
|---|---|---|
| Предметна модель | `account.withdraw(x)` | як змінюються дані |
| Бібліотеки | `list.sort()` | алгоритм |
| Java | класи, винятки | байт-код |
| JVM | купа, стеки | машинні інструкції |
| ОС | файли, потоки | драйвери, планувальник |

---

## Дірява абстракція

<div class="warn">

`Integer 127 == 127` → `true`, а `128 == 128` → `false`

Деталь реалізації (кеш) проступає назовні

</div>

<p class="fragment">Саме тому корисно розуміти рівень нижче</p>

---

## Інкапсуляція

**Дані + методи** в одному класі + **обмеження доступу** до стану

Мета — захист **інваріантів**:

+ баланс не від'ємний
+ курс від 1 до 6
+ початок періоду не пізніше кінця

---

## Без інкапсуляції

```java
static class LeakyAccount {
    public double balance;
    public List<String> history = new ArrayList<>();
}

leaky.balance = -1_000_000;   // компілятор не заперечує
leaky.history.clear();        // і сліди стерто
```

---

## З інкапсуляцією

```java [2-3|5-10|12-13|14-16]
final class BankAccount {
    private BigDecimal balance = BigDecimal.ZERO;
    private final List<String> history = new ArrayList<>();

    public void withdraw(BigDecimal amount) {
        requirePositive(amount);
        if (balance.compareTo(amount) < 0)
            throw new IllegalStateException("Недостатньо коштів");
        balance = balance.subtract(amount);
        history.add("-" + amount);
    }

    public BigDecimal getBalance() { return balance; }   // незмінний тип

    public List<String> getHistory() {
        return Collections.unmodifiableList(history);    // лише читання
    }
}
```

---

## Гетери й сетери ≠ інкапсуляція

```java [1-4|6-7]
// Погано: об'єкт — пасивний контейнер
if (account.getBalance().compareTo(amount) >= 0) {
    account.setBalance(account.getBalance().subtract(amount));
}

// Добре: Tell, don't ask
account.withdraw(amount);
```

<p class="muted fragment">Сетер має сенс, лише якщо перевіряє значення або є частиною поведінки</p>

---

## Захисні копії

```java [3-6|8]
final class LegacyPeriod {
    private final Date start, end;
    LegacyPeriod(Date start, Date end) {
        this.start = new Date(start.getTime());   // копія на вході
        this.end = new Date(end.getTime());
        if (this.start.after(this.end)) throw new IllegalArgumentException();
    }
    Date getEnd() { return new Date(end.getTime()); }   // копія на виході
}
```

```java
record ModernPeriod(LocalDate start, LocalDate end) {
    ModernPeriod {
        if (start.isAfter(end)) throw new IllegalArgumentException();
    }
}
```
<!-- element class="fragment" -->

note: Перевірка після копіювання — інакше інший потік може змінити аргумент між перевіркою та копією. Краще — незмінні типи.

---

## Чек-лист інкапсуляції

+ поля `private`
+ незмінне після створення — `final`
+ перевірка аргументів у конструкторах і мутаторах
+ назовні — `List.copyOf(...)` / `unmodifiableList(...)`
+ незмінні типи: `String`, `LocalDate`, `BigDecimal`, `record`
+ операції предметної області замість `setBalance`

---

## Абстрагування vs інкапсуляція

| | Абстрагування | Інкапсуляція |
|---|---|---|
| Питання | **що** робить об'єкт? | **як** захистити будову? |
| Рівень | проєктування | реалізація |
| Інструменти | інтерфейси, абстрактні класи, публічні методи | модифікатори, `final`, захисні копії |
| Результат | зрозуміла модель | об'єкт, який не зламати ззовні |

---

# 7. Підсумки

---

## Типові помилки

| Помилка | Як правильно |
|---|---|
| `s1 == s2` для рядків | `s1.equals(s2)` |
| `nextLine()` після `nextInt()` | додатковий `nextLine()` |
| `int[] b = a` як копія | `Arrays.copyOf(a, a.length)` |
| `double` для грошей | `BigDecimal` |
| публічні поля | `private` + методи з перевірками |
| повернення внутрішнього `List` | `List.copyOf(...)` |
| ресурс без `close()` | try-with-resources |
| розпакування `null` | перевірка або примітив |

---

## Ключові тези

+ байт-код + JVM = переносимість; JIT = швидкодія
+ статична типізація, навіть з `var`
+ примітив — значення, посилання — адреса об'єкта в купі
+ параметри — завжди за значенням
+ GC збирає недосяжне; покоління, бо більшість помирає молодими
+ `finalize()` — ні; `AutoCloseable` — так
+ інкапсуляція = захист інваріантів, а не гетери/сетери

---

## Питання для самоперевірки

1. Чому `.class` з Windows запускається на Linux?
2. Де лежить поле `int age` об'єкта `Student`?
3. Чому `swap(Point a, Point b)` не працює?
4. Що виведе `Integer a = 200, b = 200; a == b`?
5. Чи зберуть два об'єкти, що посилаються один на одного?
6. Коли компілятор створює конструктор за замовчуванням?
7. Чому «порожні» сетери — погана інкапсуляція?

---

<!-- slide bg="#1F4E79" -->

# <span style="color:white">Дякую!</span>

<span style="color:#DCE8F4">Запитання?</span>
