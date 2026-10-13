---
theme: white
highlightTheme: atom-one-light
transition: slide
width: 1280
height: 800
margin: 0.06
slideNumber: true
---

# Прагматичні принципи
### DRY · KISS · YAGNI · правило бойскаута

---

## План

1. DRY — Don't Repeat Yourself <!-- element class="fragment" -->
2. KISS — Keep It Simple, види складності та її метрики <!-- element class="fragment" -->
3. YAGNI — You Aren't Gonna Need It <!-- element class="fragment" -->
4. Правило бойскаута <!-- element class="fragment" -->

---

# DRY
## Don't Repeat Yourself

---

## DRY — визначення

Кожне **знання** має одне, однозначне представлення в системі.

```java
// OrderService
if (customer.orders() > 10) price = price * 0.9;
// InvoiceService
if (customer.orders() > 10) total = total * 0.9;
// CartView
boolean showBadge = customer.orders() > 10;
```

- Правило знижки живе в **трьох** місцях <!-- element class="fragment" -->
- Поріг змінили на 5 — оновили два місця з трьох <!-- element class="fragment" -->

---

## DRY — виправлення

```java
public final class LoyaltyPolicy {
    private static final int THRESHOLD = 10;
    private static final double DISCOUNT = 0.10;

    public static boolean isLoyal(Customer c) { return c.orders() > THRESHOLD; }

    public static double apply(Customer c, double amount) {
        return isLoyal(c) ? amount * (1 - DISCOUNT) : amount;
    }
}
```

```java
price = LoyaltyPolicy.apply(customer, price);
boolean showBadge = LoyaltyPolicy.isLoyal(customer);
```

---

## Форми дублювання

| Форма | Приклад |
|---|---|
| copy-paste логіки | однаковий розрахунок у двох сервісах |
| магічні значення | `0.2`, `"ADMIN"`, `86400` у різних файлах |
| паралельні `switch` | `switch (status)` у п'яти класах |
| похідні дані | зберігаємо і `birthDate`, і `age` |
| дублювання між шарами | однакові правила валідації в UI, сервісі, БД |
| код ↔ документація | коментар описує те, що вже змінилось у коді |

---

## Магічні значення

```java
// Погано
if (user.role().equals("ADMIN")) { ... }
if (role.equals("ADmIN")) { ... }                 // опечатка компілюється
double tax = amount * 0.2;
double gross = net + net * 0.2;
```

```java
// Добре
public enum Role { ADMIN, TEACHER, STUDENT }
if (user.role() == Role.ADMIN) { ... }            // опечатка не скомпілюється

private static final BigDecimal VAT_RATE = new BigDecimal("0.20");
```

<!-- element class="fragment" -->
`enum` і константи — **єдине джерело правди** для значень.

---

## Похідні дані

```java
// Погано: age і birthDate можуть суперечити одне одному
public record Student(String name, LocalDate birthDate, int age) {}
```

```java
// Добре: age обчислюється
public record Student(String name, LocalDate birthDate) {
    public int age(LocalDate today) {
        return Period.between(birthDate, today).getYears();
    }
}
```

<!-- element class="fragment" -->
Те саме для `total` замовлення, `count` елементів, `fullName = first + last`.

---

## Copy-paste з варіацією

```java
// Погано
String studentsCsv(List<Student> list) {
    var sb = new StringBuilder("name;group\n");
    for (var s : list) sb.append(s.name()).append(';').append(s.group()).append('\n');
    return sb.toString();
}

String teachersCsv(List<Teacher> list) {
    var sb = new StringBuilder("name;department\n");
    for (var t : list) sb.append(t.name()).append(';').append(t.department()).append('\n');
    return sb.toString();
}
```

```java
// Добре: різниця винесена в параметри
<T> String toCsv(String header, List<T> rows, Function<T, String> line) {
    return header + "\n" + rows.stream().map(line).collect(Collectors.joining("\n"));
}

toCsv("name;group",      students, s -> s.name() + ";" + s.group());
toCsv("name;department", teachers, t -> t.name() + ";" + t.department());
```
<!-- element class="fragment" -->

---

## Паралельні `switch`

```java
// у DeliveryCost
switch (type) { case COURIER -> 150; case POST -> 70; ... }
// у DeliveryTime
switch (type) { case COURIER -> 1;   case POST -> 3;  ... }
// у DeliveryLabel
switch (type) { case COURIER -> "Кур'єр"; case POST -> "Пошта"; ... }
```

```java
public enum DeliveryType {
    COURIER(150, 1, "Кур'єр"),
    POST(70, 3, "Пошта");

    private final int cost, days;
    private final String label;

    DeliveryType(int cost, int days, String label) {
        this.cost = cost; this.days = days; this.label = label;
    }
}
```
<!-- element class="fragment" -->

<!-- element class="fragment" -->
Новий тип доставки — **один** рядок замість трьох правок.

---

## Антипатерн: хибний DRY

```java
if (name.length() > 20) throw ...;    // ім'я користувача
if (title.length() > 20) throw ...;   // назва товару
```

- Однаковий **текст** ≠ однакове **знання** <!-- element class="fragment" -->
- Ліміти збіглись випадково — завтра розійдуться <!-- element class="fragment" -->
- Спільний метод `checkLength20()` зв'яже дві незалежні речі <!-- element class="fragment" -->

---

## Антипатерн: абстракція з прапорцями

Спільний метод "обростає" умовами під кожного клієнта:

```java
String format(Order o, boolean forEmail, boolean withTax,
              boolean shortVersion, boolean isAdmin) {
    var sb = new StringBuilder();
    if (!shortVersion) sb.append(o.header());
    if (withTax && !isAdmin) sb.append(o.tax());
    if (forEmail) sb.append("<br>"); else sb.append("\n");
    ...
}
```

- Кожен виклик — `format(o, true, false, true, false)`: незрозуміло, що відбувається <!-- element class="fragment" -->
- Зміна для одного клієнта ламає інших <!-- element class="fragment" -->
- Краще повернути **окремі методи**, ніж тримати таку "спільну" абстракцію <!-- element class="fragment" -->

note: Sandi Metz: "duplication is far cheaper than the wrong abstraction".

---

## DRY — best practices

- **Правило трьох**: двічі — терпимо, на третьому — виносимо <!-- element class="fragment" -->
- Виносимо **знання** (правило, формула, константа), а не схожий текст <!-- element class="fragment" -->
- Значення — в `enum` / константи / конфігурацію <!-- element class="fragment" -->
- Похідні дані — обчислювати, а не зберігати <!-- element class="fragment" -->
- Схема БД, DTO, API-контракт — генерувати з одного джерела, де можливо <!-- element class="fragment" -->
- У **тестах** допустимо більше повторень: тест має читатися сам по собі (DAMP — *Descriptive And Meaningful Phrases*) <!-- element class="fragment" -->

---

# KISS
## Keep It Simple, Stupid

---

## KISS — визначення

Найпростіше рішення, яке **працює** і яке **легко змінити**.

```java
// Переускладнено
boolean isEven = IntStream.of(n).mapToObj(BigInteger::valueOf)
        .map(b -> b.mod(BigInteger.TWO)).anyMatch(BigInteger.ZERO::equals);

// Просто
boolean isEven = n % 2 == 0;
```

<!-- element class="fragment" -->
Простий ≠ примітивний. Простий = мало частин, мало зв'язків, очевидна поведінка.

---

## Два види складності

|                 | Суттєва          | Випадкова             |
| --------------- | ---------------- | --------------------- |
| Звідки          | з самої задачі   | з наших рішень        |
| Приклад         | правила податків | дублікати, зайві шари |
| Можна прибрати? | ні               | так                   |

<!-- element class="fragment" -->
Головна вартість коду — **зміна**, а не написання. KISS бореться саме з випадковою складністю.

note: Ф. Брукс, "No Silver Bullet" (1986). "The Pragmatic Programmer" — Гант і Томас, критерій ETC (Easier To Change).

---

## Як виміряти складність коду

| Метрика | Що показує | Автор |
|---|---|---|
| **Цикломатична** | скільки незалежних шляхів виконання є в методі | Т. Маккейб, 1976 |
| **Когнітивна** | наскільки важко методу **зрозуміти людині** | SonarSource, 2017 |

<!-- element class="fragment" -->
Обидві рахуються **для методу** і допомагають знайти місця, які варто спростити.

---

## Цикломатична складність

**M = кількість точок розгалуження + 1**

Точки розгалуження: `if`, `else if`, `for`, `while`, `do`, `case`, `catch`, `&&`, `||`, `?:`

```java
String grade(int score) {              // 1 (базова)
    if (score < 0 || score > 100)      // +1 if, +1 ||
        throw new IllegalArgumentException();
    if (score >= 90) return "A";       // +1
    if (score >= 75) return "B";       // +1
    if (score >= 60) return "C";       // +1
    return "F";
}                                      // M = 6
```

<!-- element class="fragment" -->
M — мінімальна кількість тестів, щоб пройти **кожен** шлях хоча б раз.

---

## Цикломатична: пороги

| M | Оцінка |
|---|---|
| 1–10 | простий метод |
| 11–20 | складний, варто спростити |
| 21–50 | дуже складний, важко тестувати |
| > 50 | нетестовний |

Недолік метрики: <!-- element class="fragment" -->
- `switch` на 10 гілок і 10 вкладених `if` дають **однакове** M <!-- element class="fragment" -->
- а читати їх — зовсім не однаково важко <!-- element class="fragment" -->

---

## Когнітивна складність

Рахує, наскільки код **ламає лінійне читання**:

| Правило | |
|---|---|
| `if`, `else if`, `else`, `for`, `while`, `catch`, `switch`, `?:` | +1 |
| послідовність `&&` / `||` (кожна зміна оператора) | +1 |
| `break`/`continue` на мітку, рекурсія | +1 |
| **кожен рівень вкладеності** для структури всередині іншої | +1 за рівень |
| `switch` цілком (незалежно від кількості `case`) | +1 |
| ранній `return` | 0 |

<!-- element class="fragment" -->
Головна відмінність: **вкладеність штрафується**.

---

## Однакова цикломатична, різна когнітивна

```java
String dayName(int d) {                // цикломатична: 8
    return switch (d) {                // когнітивна: +1
        case 1 -> "Пн";  case 2 -> "Вт";  case 3 -> "Ср";
        case 4 -> "Чт";  case 5 -> "Пт";  case 6 -> "Сб";
        case 7 -> "Нд";
        default -> throw new IllegalArgumentException();
    };
}                                      // когнітивна = 1
```

```java
int sumPrimes(int max) {                       // цикломатична: 4
    int total = 0;
    outer:
    for (int i = 2; i <= max; i++) {           // +1
        for (int j = 2; j < i; j++) {          // +2 (вкладеність 1)
            if (i % j == 0) {                  // +3 (вкладеність 2)
                continue outer;                // +1
            }
        }
        total += i;
    }
    return total;
}                                              // когнітивна = 7
```
<!-- element class="fragment" -->

---

## Як знизити складність

```java
// когнітивна = 6
double discount(Customer c, Order o) {
    if (c.isActive()) {                        // +1
        if (o.total() > 1000) {                // +2
            return c.isVip() ? 0.15 : 0.10;    // +3
        }
    }
    return 0;
}
```

```java
// когнітивна = 3
double discount(Customer c, Order o) {
    if (!c.isActive())     return 0;           // +1
    if (o.total() <= 1000) return 0;           // +1
    return c.isVip() ? 0.15 : 0.10;            // +1
}
```
<!-- element class="fragment" -->

Прийоми: ранній `return`, винесення методу, `switch`-вирази, Stream API замість вкладених циклів, поліморфізм замість ланцюжка `if`. <!-- element class="fragment" -->

---

## Власний велосипед

```java
// Погано
boolean isLeapYear(int y) {
    return (y % 4 == 0 && y % 100 != 0) || y % 400 == 0;
}
int daysBetween(int d1, int m1, int y1, int d2, int m2, int y2) { /* 40 рядків */ }
```

```java
// Добре
Year.isLeap(2028);
ChronoUnit.DAYS.between(start, end);
```

| Задача | Стандартне рішення |
|---|---|
| дати, часові пояси | `java.time` |
| сортування, пошук | `Collections`, `List.sort`, Stream API |
| рядки | `String.join`, `String.repeat`, `strip()` |
| JSON | Jackson (лекція 12) |
| гроші | `BigDecimal`, а не `double` |

---

## "Розумний" однорядник

```java
// Погано
return list.stream().collect(Collectors.groupingBy(s -> s.grade() >= 60,
        Collectors.mapping(Student::name, Collectors.collectingAndThen(
        Collectors.toList(), l -> l.isEmpty() ? List.of("—") : l)))).get(true);
```

```java
// Добре
List<String> passed = list.stream()
        .filter(s -> s.grade() >= 60)
        .map(Student::name)
        .toList();

return passed.isEmpty() ? List.of("—") : passed;
```
<!-- element class="fragment" -->

<!-- element class="fragment" -->
Короткий код ≠ простий код. Проміжні змінні з назвами — це документація.

---

## Передчасна оптимізація

```java
// "Оптимізовано"
int idx = (hash ^ (hash >>> 16)) & (table.length - 1);
String key = new StringBuilder(64).append(a).append('|').append(b).toString().intern();
```

```java
// Просто
Map<Key, Value> cache = new HashMap<>();
record Key(String a, String b) {}
```

- Оптимізують **без вимірювань** — і не те місце <!-- element class="fragment" -->
- Код стає незрозумілим, а виграш — мікросекунди <!-- element class="fragment" -->
- Порядок: працює → правильно → **виміряли профайлером** → оптимізуємо вузьке місце <!-- element class="fragment" -->

note: Д. Кнут: "premature optimization is the root of all evil". Профайлери: IntelliJ Profiler, JFR, JMH для мікробенчмарків.

---

## KISS — антипатерни

| Антипатерн | Приклад |
|---|---|
| зайві шари | `Controller → Service → Manager → Helper → Repository` для CRUD |
| абстракції заради абстракцій | інтерфейс і базовий клас для єдиної реалізації |
| generic-пекло | `Processor<T extends Handler<? super R>, R>` |
| власний фреймворк | "свій маленький Spring" для лабораторної |
| конфігурація всього | 30 параметрів у `application.yml`, які ніхто не змінює |
| булеві параметри | `send(msg, true, false, true)` |

---

## KISS — best practices

- Назви, що пояснюють намір: `isEligibleForScholarship()`, а не `check2()` <!-- element class="fragment" -->
- Короткі методи з одним рівнем абстракції <!-- element class="fragment" -->
- Guard clauses замість вкладених `if` <!-- element class="fragment" -->
- Стандартна бібліотека раніше за власний код <!-- element class="fragment" -->
- `record`, `enum`, `switch`-вирази — менше коду для типових задач <!-- element class="fragment" -->
- Оптимізація — лише після вимірювань <!-- element class="fragment" -->

---

# YAGNI
## You Aren't Gonna Need It

---

## YAGNI — визначення

Не реалізуй функціональність, поки вона **реально** не потрібна.

```java
public interface PaymentProvider { ... }
public abstract class AbstractPaymentProvider implements PaymentProvider { ... }
public class PaymentProviderRegistry { ... }
public class PaymentProviderConfig { ... }
public class LiqPayProvider extends AbstractPaymentProvider { ... }  // єдина
```

<!-- element class="fragment" -->
Через рік друга платіжна система так і не з'явилась, а 5 класів доводиться підтримувати.

---

## Гнучкість "на всяк випадок"

```java
// Погано
public List<Student> find(String name, String group, Integer year,
                          Boolean active, String sortField, boolean asc,
                          int page, int size, Locale locale, boolean includeDeleted) { ... }

// Використовується лише так:
find(null, "КН-21", null, null, null, true, 0, 1000, null, false);
```

```java
// Добре: те, що потрібно зараз
public List<Student> findByGroup(String group) { ... }
```
<!-- element class="fragment" -->

<!-- element class="fragment" -->
Новий фільтр — новий метод, **коли** він знадобиться.

---

## Більше прикладів

| "Колись знадобиться" | Що отримали |
|---|---|
| підтримка 5 мов інтерфейсу | застосунок лише для українських студентів |
| мікросервіси з першого дня | 6 сервісів, 1 розробник, 20 користувачів |
| `GenericRepository<T, ID>` для всіх сутностей | 2 сутності з різною логікою |
| поле `extraData: Map<String, Object>` | ніхто не знає, що в ньому лежить |
| плагінна система | жодного плагіна |

---

## Ціна фічі на майбутнє

| Вартість | Що це |
|---|---|
| **Побудови** | час на код, який не знадобився |
| **Затримки** | корисні фічі, яких не зробили за цей час |
| **Супроводу** | кожна зміна мусить враховувати зайвий код |
| **Виправлення** | реальна вимога приходить **іншою**, ніж передбачили |

note: Класифікація з есе Мартіна Фаулера "Yagni" (2015).

---

## Антипатерн: мертвий код

```java
public class ReportService {
    // public void exportToXml(...) { ... }        // може знадобиться
    // public void exportToYaml(...) { ... }

    @Deprecated
    public void oldExport(...) { ... }              // ніхто не викликає

    private void prepareForV2() { }                 // порожній
}
```

- Закоментований і невикористаний код — **шум** при кожному читанні <!-- element class="fragment" -->
- Історія зберігається в **Git** — видаляйте сміливо <!-- element class="fragment" -->
- IntelliJ підсвічує невикористаний код сірим: *Analyze → Inspect Code → Unused declaration* <!-- element class="fragment" -->

---

## YAGNI ≠ писати абияк

| Відкладаємо | Робимо одразу |
|---|---|
| фічі "на майбутнє" | читабельний код |
| абстракції під уявні варіанти | тести |
| налаштування, які ніхто не змінює | обробку помилок |
| оптимізацію без вимірювань | безпеку (паролі, SQL-ін'єкції) |
| | продуману схему даних |

<!-- element class="fragment" -->
Чистий протестований код **легко розширити**, коли потреба справді з'явиться.

---

## YAGNI — best practices

- Реалізуйте **поточну** вимогу, а не уявну <!-- element class="fragment" -->
- Інтерфейс — коли з'являється **друга** реалізація (або фейк для тестів) <!-- element class="fragment" -->
- Параметр — коли з'являється **другий** варіант значення <!-- element class="fragment" -->
- Видаляйте мертвий і закоментований код <!-- element class="fragment" -->
- Дорогі для зміни рішення (схема БД, публічний API) — продумуйте заздалегідь <!-- element class="fragment" -->

---

# Правило бойскаута

---

## Правило бойскаута — визначення

Залиш код трохи чистішим, ніж він був до тебе.

- Невеликі покращення **поруч** зі зміною, яку робите <!-- element class="fragment" -->
- Код поступово стає кращим без окремих "великих рефакторингів" <!-- element class="fragment" -->

---

## Приклад: до

Задача — виправити баг: біля півночі штраф рахується неправильно.

```java
public int calc(Loan l) {
    // int old = (int)((System.currentTimeMillis() - l.d) / 86400000);
    long x = (System.currentTimeMillis() - l.d) / 86400000;
    if (x > 14) {
        return (int)(x - 14) * 5;
    }
    return 0;
}
```

---

## Приклад: після

```java
private static final int FREE_DAYS = 14;
private static final int FINE_PER_DAY = 5;

public int calculateFine(Loan loan, LocalDate today) {
    long daysOnHand = ChronoUnit.DAYS.between(loan.takenAt(), today);
    long overdueDays = daysOnHand - FREE_DAYS;
    return overdueDays > 0 ? (int) overdueDays * FINE_PER_DAY : 0;
}
```

```java
@Test
void fineStartsOnFifteenthDay() {
    var loan = new Loan(LocalDate.of(2026, 10, 1));
    assertEquals(0, calculateFine(loan, LocalDate.of(2026, 10, 15)));
    assertEquals(5, calculateFine(loan, LocalDate.of(2026, 10, 16)));
}
```

- баг виправлено + тест на нього <!-- element class="fragment" -->
- назви, константи, `java.time` замість мілісекунд <!-- element class="fragment" -->
- поточна дата — параметр, тест детермінований <!-- element class="fragment" -->

---

## Типові дрібні покращення

| Що | Як в IntelliJ IDEA |
|---|---|
| перейменувати `d`, `x`, `tmp` | *Refactor → Rename* |
| винести магічне число | *Refactor → Introduce Constant* |
| розбити довгий метод | *Refactor → Extract Method* |
| прибрати невикористаний імпорт / код | *Code → Optimize Imports* |
| спростити умову | *Alt+Enter* → підказки інспекцій |
| додати тест на виправлений баг | *Generate → Test* |

<!-- element class="fragment" -->
Автоматичні рефакторинги IDE безпечніші за ручні правки.

---

## Антипатерни

| Антипатерн | Наслідок |
|---|---|
| переписати пів модуля в PR "fix typo" | рев'ю неможливе, ризик регресій |
| рефакторинг і зміна поведінки в одному коміті | не видно, що саме змінилось |
| рефакторинг без тестів | непомітно зламана поведінка |
| "не мій код — не чіпаю" | "розбиті вікна": безлад накопичується |
| змінювати стиль усього файлу (форматування) | дифф на 500 рядків заради 1 правки |

note: Теорія розбитих вікон — з "The Pragmatic Programmer": одна неприбрана проблема провокує нові.

---

## Best practices

- Покращуйте лише код, який **і так змінюєте** <!-- element class="fragment" -->
- Спочатку тест, потім рефакторинг <!-- element class="fragment" -->
- Рефакторинг і зміна поведінки — **окремими комітами** <!-- element class="fragment" -->
- Великий рефакторинг — окремою задачею і окремим PR <!-- element class="fragment" -->
- Форматування — автоматично для всього проєкту (`.editorconfig`, форматер у CI), а не вручну <!-- element class="fragment" -->

---

## Коли принципи конфліктують

| Конфлікт | Як вирішувати |
|---|---|
| DRY vs KISS | спільна абстракція складніша за дублікат → лишаємо дублікат |
| DRY vs YAGNI | не виносимо "спільне" для одного використання |
| KISS vs продуктивність | спершу просто, оптимізуємо після вимірювань |
| бойскаут vs рев'ю | дрібне — в тому ж PR, велике — окремо |

---

## Підсумок

- **DRY** — одне знання в одному місці; виносимо правила, а не схожий текст <!-- element class="fragment" -->
- **KISS** — найпростіше рішення, що працює; стежимо за цикломатичною і когнітивною складністю <!-- element class="fragment" -->
- **YAGNI** — реалізуємо поточну вимогу, а не уявну <!-- element class="fragment" -->
- **Правило бойскаута** — дрібні покращення поруч зі зміною, окремими комітами <!-- element class="fragment" -->

---

# Питання?
