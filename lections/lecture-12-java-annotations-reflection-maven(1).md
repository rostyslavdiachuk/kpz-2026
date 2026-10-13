---
theme: white
highlightTheme: atom-one-light
transition: slide
width: 1280
height: 800
margin: 0.06
---

# Анотації, Reflection та Maven
### Метадані · рефлексія · залежності

note: Спрощена версія. Глибокі деталі (байткод, MethodHandle, BOM, parent POM) винесено в нотатки — можна згадати усно, якщо група сильна.

---

## План

1. Анотації: що це і навіщо <!-- element class="fragment" -->
2. Reflection: як програма "бачить" сама себе <!-- element class="fragment" -->
3. Створення об'єктів і виклик методів через рефлексію <!-- element class="fragment" -->
4. Анотації + Reflection: пишемо власний валідатор <!-- element class="fragment" -->
5. Annotation Processing — коротко <!-- element class="fragment" -->
6. Maven: як підключати бібліотеки <!-- element class="fragment" -->
7. Gradle — одним слайдом <!-- element class="fragment" -->
8. Практика <!-- element class="fragment" -->

---

# Частина 1
## Анотації

---

## Ви їх уже бачили

```java
@Override
public String toString() { return "User"; }

@Deprecated
public void oldMethod() { }

@FunctionalInterface
interface Calculator { int calc(int a, int b); }
```

- Анотація — це **мітка** з `@`, яку ставлять над класом, полем або методом <!-- element class="fragment" -->
- Сама по собі вона **нічого не робить** <!-- element class="fragment" -->
- Її хтось **читає**: компілятор, IDE, фреймворк або наш власний код <!-- element class="fragment" -->

---

## Навіщо власні анотації?

Без анотацій перевірки живуть усередині моделі:

```java
public record UserProfile(String username, String biography) {
    public UserProfile {
        if (username.length() > 20) throw new IllegalArgumentException("Задовге ім'я");
        if (biography != null && biography.length() > 250) throw new IllegalArgumentException("...");
    }
}
```

- Модель **змішана** з правилами валідації <!-- element class="fragment" -->
- Хочеться просто **позначити** поле: "не довше 20 символів" <!-- element class="fragment" -->
- А перевіряти — **в окремому місці** <!-- element class="fragment" -->

---

## З анотаціями

```java
public record UserProfile(
        @MaxLength(20)  String username,
        @MaxLength(250) String biography
) {}
```

<!-- element class="fragment" -->
Модель лише **несе мітки**. Хто і як їх перевірить — не її справа.

<!-- element class="fragment" -->
> У C# це називається **атрибути**: `[StringLengthValidator(20)]`. Ідея та сама.

---

## Як оголосити анотацію

```java
import java.lang.annotation.*;

@Retention(RetentionPolicy.RUNTIME)       // 1. доступна під час роботи програми
@Target(ElementType.RECORD_COMPONENT)     // 2. ставиться на компоненти record
public @interface MaxLength {
    int value();                          // параметр анотації
}
```

- `@interface` — ключове слово для оголошення анотації <!-- element class="fragment" -->
- `int value()` — схоже на метод, але це **параметр** <!-- element class="fragment" -->
- Якщо параметр називається `value`, можна писати коротко: `@MaxLength(20)` <!-- element class="fragment" -->

---

## Параметри анотації

```java
public @interface MaxLength {
    int value();
    String message() default "Перевищено довжину";   // має значення за замовчуванням
}

@MaxLength(20)                                         // message — за замовчуванням
@MaxLength(value = 250, message = "Задовга біографія") // обидва явно
```

Типи параметрів — лише прості: примітиви, `String`, `enum`, `Class` або масиви з них.

<!-- element class="fragment" -->
Значення мають бути **константами** — `@MaxLength(getLimit())` не скомпілюється.

---

## Дві мета-анотації, які треба знати

**`@Target`** — **куди** можна ставити:

| Значення | Куди |
|---|---|
| `TYPE` | на клас, інтерфейс, record |
| `FIELD` | на поле |
| `METHOD` | на метод |
| `RECORD_COMPONENT` | на компонент record |

**`@Retention`** — **як довго** живе:

| Значення | Хто бачить |
|---|---|
| `SOURCE` | лише компілятор (як `@Override`) |
| `CLASS` | **за замовчуванням** — лежить у `.class`, але програма не бачить |
| `RUNTIME` | програма під час роботи ✅ |

---

## Головна пастка

```java
public @interface MaxLength {     // забули @Retention!
    int value();
}
```

<!-- element class="fragment" -->
- Код компілюється, помилок немає <!-- element class="fragment" -->
- Але програма анотацію **не бачить** — валідація "проходить" для всього <!-- element class="fragment" -->

<!-- element class="fragment" -->
> Пишете анотацію для читання в рантаймі — **завжди** додавайте `@Retention(RetentionPolicy.RUNTIME)`.

---

## Де це в реальних проєктах

```java
@RestController                          // Spring: це веб-контролер
public class UserController {

    @GetMapping("/users/{id}")           // Spring: обробляє GET /users/5
    public User get(@PathVariable long id) { ... }
}

public record UserDto(
    @NotBlank @Size(max = 20) String username,    // валідація
    @JsonProperty("user_id") long id              // назва поля в JSON
) {}

class UserTest {
    @Test                                // JUnit: це тест
    void createsUser() { ... }
}
```

<!-- element class="fragment" -->
Ми пишемо **лише мітки** — всю роботу роблять бібліотеки.

---

# Частина 2
## Reflection

---

## Проблема

Як JUnit знаходить **ваші** методи з `@Test`?
Як Jackson перетворює **ваш** клас у JSON?

- Ці бібліотеки написані **задовго** до вашого коду <!-- element class="fragment" -->
- Вони не знають ваших класів при компіляції <!-- element class="fragment" -->
- Їм потрібно **під час роботи програми** дізнатися: які поля, які методи, які анотації <!-- element class="fragment" -->

<!-- element class="fragment" -->
**Reflection** (рефлексія) — можливість програми досліджувати власну структуру під час виконання.

---

## Точка входу — `Class`

```java
Class<?> c1 = String.class;                    // знаємо тип у коді
Class<?> c2 = "hello".getClass();              // маємо об'єкт
Class<?> c3 = Class.forName("java.util.UUID"); // маємо лише назву (рядок)
```

Об'єкт `Class` описує тип: його поля, методи, конструктори, анотації.

<!-- element class="fragment" -->

| Клас | Описує |
|---|---|
| `Field` | поле |
| `Method` | метод |
| `Constructor` | конструктор |
| `RecordComponent` | компонент record |
<!-- element class="fragment" -->

---

## Подивимось на клас

```java
public class TestUser {
    private int id;
    protected String passwordHash;
    private String username;

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    private void calculateHash(String salt, int iterations) { }
}
```

---

## Поля

```java
Class<?> type = TestUser.class;

for (Field f : type.getDeclaredFields()) {
    IO.println(f.getType().getSimpleName() + " " + f.getName());
}
```

```text
int id
String passwordHash
String username
```
<!-- element class="fragment" -->

<!-- element class="fragment" -->
`getDeclaredFields()` — **усі** поля цього класу, навіть `private`.

---

## Методи

```java
for (Method m : type.getDeclaredMethods()) {
    IO.println(m.getReturnType().getSimpleName() + " " + m.getName()
            + " — параметрів: " + m.getParameterCount());
}
```

```text
String getUsername — параметрів: 0
void setUsername — параметрів: 1
void calculateHash — параметрів: 2
```
<!-- element class="fragment" -->

<!-- element class="fragment" -->
⚠️ Порядок методів **не гарантовано** — не покладайтесь на нього.

note: Якщо студенти спитають: є ще getFields()/getMethods() — вони повертають лише public, але разом з успадкованими (і методи Object). Імена параметрів (salt, iterations) рефлексія бачить лише якщо компілювати з -parameters, інакше arg0, arg1.

---

## Загальна інформація про тип

```java
IO.println("Ім'я: " + type.getSimpleName());
IO.println("Пакет: " + type.getPackageName());
IO.println("Батьківський клас: " + type.getSuperclass().getSimpleName());
IO.println("Інтерфейс? " + type.isInterface());
IO.println("Record? " + type.isRecord());
```

```text
Ім'я: TestUser
Пакет: ua.chnu.lecture12
Батьківський клас: Object
Інтерфейс? false
Record? false
```
<!-- element class="fragment" -->

---

## Типова помилка: назви рядками

```java
Method m = type.getMethod("calculateTotal");
```

- Перейменували метод у IDE — рядок `"calculateTotal"` **не змінився** <!-- element class="fragment" -->
- Компілятор мовчить → помилка `NoSuchMethodException` лише **під час роботи** <!-- element class="fragment" -->

<!-- element class="fragment" -->
**Краще** — шукати не за назвою, а **за анотацією**:

```java
for (Method m : type.getDeclaredMethods()) {
    if (m.isAnnotationPresent(Test.class)) { ... }
}
```
<!-- element class="fragment" -->

---

## Рефлексія — повільна

- Кожен виклик `getDeclaredFields()` створює **нові** масиви й об'єкти <!-- element class="fragment" -->
- Робити це в циклі на кожен запит — марнування пам'яті й часу <!-- element class="fragment" -->

<!-- element class="fragment" -->
**Правило:** дослідили тип **один раз** — запам'ятали результат.

```java
private static final Map<Class<?>, Field[]> CACHE = new ConcurrentHashMap<>();

static Field[] fieldsOf(Class<?> type) {
    return CACHE.computeIfAbsent(type, Class::getDeclaredFields);
}
```
<!-- element class="fragment" -->

note: Для просунутих: у JDK є спеціальний клас ClassValue саме для такого кешу — він не тримає ClassLoader і не створює витоків пам'яті в серверах застосунків.

---

# Частина 3
## Створюємо об'єкти і викликаємо методи

---

## Динамічна робота

Мало **знати** структуру — інколи треба **діяти**:

- Spring створює ваші сервіси, знаючи лише їхній клас <!-- element class="fragment" -->
- JUnit створює об'єкт тестового класу і викликає кожен `@Test` <!-- element class="fragment" -->

| Що треба | Як |
|---|---|
| Створити об'єкт | `type.getDeclaredConstructor().newInstance()` |
| Викликати метод | `method.invoke(об'єкт, аргументи...)` |
| Прочитати поле | `field.get(об'єкт)` |
<!-- element class="fragment" -->

---

## Приклад

```java
// Назву класу могли прочитати з файлу конфігурації
Class<?> type = Class.forName("ua.chnu.lecture12.TestUser");

// Створюємо об'єкт (конструктор без параметрів)
Object user = type.getDeclaredConstructor().newInstance();

// Знаходимо метод: назва + типи параметрів
Method setter = type.getMethod("setUsername", String.class);
setter.invoke(user, "Dynamic_Administrator");

Method getter = type.getMethod("getUsername");
IO.println(getter.invoke(user));   // Dynamic_Administrator
```

<!-- element class="fragment" -->
Зверніть увагу: змінна `user` має тип `Object` — компілятор нічого не знає про `TestUser`.

---

## Винятки при `invoke`

```java
try {
    method.invoke(user);
} catch (InvocationTargetException e) {
    IO.println("Метод кинув: " + e.getCause());   // справжня причина тут!
}
```

- Якщо **сам метод** кинув виняток — рефлексія загортає його в `InvocationTargetException` <!-- element class="fragment" -->
- Справжній виняток — у `e.getCause()` <!-- element class="fragment" -->

---

## Антипатерн: злам `private`

```java
Field f = SomeLibrary.class.getDeclaredField("secretCache");
f.setAccessible(true);      // відкрили private
f.set(library, null);       // "полагодили" бібліотеку 🙃
```

- Рефлексія дозволяє обійти `private` — це **порушення інкапсуляції** <!-- element class="fragment" -->
- Автор бібліотеки перейменує поле в новій версії — ваша програма впаде <!-- element class="fragment" -->
- Для класів самої Java це вже **заборонено** — отримаєте `InaccessibleObjectException` <!-- element class="fragment" -->

<!-- element class="fragment" -->
> `setAccessible(true)` — лише для власного коду і тестів, ніколи для чужих бібліотек.

---

## Наскільки це повільно?

| Спосіб | Швидкість | Складність |
|---|---|---|
| Звичайний виклик `user.getUsername()` | 🟢 максимальна | 🟢 |
| `method.invoke(user)` | 🔴 у рази повільніше | 🟢 |

Чому повільно: <!-- element class="fragment" -->
- аргументи пакуються в масив `Object[]` <!-- element class="fragment" -->
- `int` перетворюється на `Integer` і назад (boxing) <!-- element class="fragment" -->
- JVM не може оптимізувати виклик, бо не знає заздалегідь, що викликається <!-- element class="fragment" -->

<!-- element class="fragment" -->
> Рефлексія — для налаштування і старту програми, а не для коду, що виконується мільйони разів.

note: Для сильних студентів: швидкі альтернативи — MethodHandle (java.lang.invoke) у static final полі, LambdaMetafactory, генерація байткоду (ByteBuddy, Class-File API з Java 24). Аналоги в .NET: Delegate.CreateDelegate, Expression Trees, Reflection.Emit.

---

# Частина 4
## Анотації + Reflection

---

## Анотаціям потрібен "рушій"

`@MaxLength(20)` сама нічого не перевірить. Потрібен код, який:

1. пройде по всіх компонентах record'а <!-- element class="fragment" -->
2. знайде ті, що позначені `@MaxLength` <!-- element class="fragment" -->
3. дістане фактичне значення <!-- element class="fragment" -->
4. порівняє з лімітом <!-- element class="fragment" -->

<!-- element class="fragment" -->
Саме так працюють валідатори, JUnit, Spring.

---

## Читання анотації

```java
MaxLength rule = component.getAnnotation(MaxLength.class);

if (rule != null) {                  // null — анотації немає
    int limit = rule.value();        // 20
    String msg = rule.message();     // "Перевищено довжину"
}
```

Метод `getAnnotation` є в `Class`, `Field`, `Method`, `RecordComponent`.

---

## Рушій валідації

```java
public class ValidationEngine {

    public static List<String> validate(Record entity) throws ReflectiveOperationException {
        List<String> errors = new ArrayList<>();

        for (RecordComponent rc : entity.getClass().getRecordComponents()) {  // 1
            MaxLength rule = rc.getAnnotation(MaxLength.class);               // 2
            if (rule == null) continue;

            Object value = rc.getAccessor().invoke(entity);                   // 3

            if (value instanceof String s && s.length() > rule.value()) {     // 4
                errors.add(rc.getName() + ": " + rule.message()
                        + " (ліміт " + rule.value() + ")");
            }
        }
        return errors;
    }
}
```

`rc.getAccessor()` — метод-геттер компонента, наприклад `username()`.

---

## Перевіряємо

```java
var profile = new UserProfile("a_very_long_username_indeed", "Java dev");

for (String error : ValidationEngine.validate(profile)) {
    IO.println(error);
}
```

```text
username: Перевищено довжину (ліміт 20)
```
<!-- element class="fragment" -->

<!-- element class="fragment" -->
- `UserProfile` нічого не знає про валідацію — лише мітки
- Уся логіка в одному місці — `ValidationEngine`
- Новий record з `@MaxLength` — працює автоматично

---

# Частина 5
## Annotation Processing — коротко

---

## А можна без рефлексії?

Мінуси рефлексії:
- повільно <!-- element class="fragment" -->
- помилки видно лише **під час роботи**: `@MaxLength(-5)` скомпілюється спокійно <!-- element class="fragment" -->

<!-- element class="fragment" -->
**Процесор анотацій** — програма, яка запускається **під час компіляції** (`javac`) і:
- перевіряє анотації → може видати **помилку компіляції** <!-- element class="fragment" -->
- генерує **новий** Java-код <!-- element class="fragment" -->

<!-- element class="fragment" -->
> У C# аналог — Source Generators.

---

## Як це виглядає для вас

```java
public record Product(@MaxLength(-5) String title) {}
```

```text
[ERROR] Product.java:[1,26] @MaxLength має бути > 0
[INFO] BUILD FAILURE
```
<!-- element class="fragment" -->

<!-- element class="fragment" -->
Відомі бібліотеки на процесорах анотацій:

| Бібліотека | Що робить |
|---|---|
| **Lombok** | генерує геттери, сеттери, конструктори |
| **MapStruct** | генерує перетворення DTO ↔ Entity |
| **Dagger** | збирає залежності (DI) без рефлексії |

note: Писати власний процесор — тема для окремої лекції (AbstractProcessor, RoundEnvironment, Messager, Filer). Lombok формально процесор, але змінює вже існуючі класи через внутрішні API javac, тому часто ламається з новими JDK.

---

## Reflection чи процесор?

| | Reflection | Процесор анотацій |
|---|---|---|
| Коли працює | під час роботи програми | під час компіляції |
| Швидкість | повільніше | як звичайний код |
| Помилки видно | у рантаймі | при компіляції |
| Складність написання | 🟢 проста | 🔴 складна |

---

# Частина 6
## Maven

---

## Проблема: чужі бібліотеки

Потрібна бібліотека для JSON. Як було колись:

1. Знайти сайт, завантажити `jackson.jar` <!-- element class="fragment" -->
2. Покласти в папку `lib/` і закомітити в Git <!-- element class="fragment" -->
3. Виявити, що Jackson потребує ще 2 бібліотеки… а ті — ще інших <!-- element class="fragment" -->
4. Дві бібліотеки хочуть **різні версії** третьої 😱 <!-- element class="fragment" -->

<!-- element class="fragment" -->
Це називають **JAR Hell** — "пекло JAR-файлів".

---

## Maven

- Інструмент для **збирання** проєкту і **управління залежностями** <!-- element class="fragment" -->
- Ви пишете, **що** потрібно, — Maven сам завантажує це і все, від чого воно залежить <!-- element class="fragment" -->
- Бібліотеки беруться з **Maven Central** — величезного публічного сховища <!-- element class="fragment" -->

<!-- element class="fragment" -->
> Аналог NuGet у .NET або npm у JavaScript.

---

## Структура проєкту

```text
my-app/
├── pom.xml                ← опис проєкту і залежностей
├── src/
│   ├── main/java/         ← ваш код
│   ├── main/resources/    ← конфіги, файли
│   └── test/java/         ← тести
└── target/                ← результат збирання (створює Maven)
```

<!-- element class="fragment" -->
Структура **однакова** в усіх Maven-проєктах — відкрили будь-який і одразу орієнтуєтесь.

---

## Як знайти бібліотеку

Кожна бібліотека має три "координати" (**GAV**):

```text
com.fasterxml.jackson.core : jackson-databind : 2.18.2
       groupId                 artifactId        version
       (хто зробив)            (що саме)         (яка версія)
```

<!-- element class="fragment" -->
Знайти можна на **central.sonatype.com** або **mvnrepository.com** — там одразу є готовий XML для копіювання.

---

## `pom.xml`

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>

    <groupId>ua.chnu.se</groupId>              <!-- наш проєкт -->
    <artifactId>lecture-12</artifactId>
    <version>1.0.0</version>

    <properties>
        <maven.compiler.release>25</maven.compiler.release>   <!-- версія Java -->
    </properties>

    <dependencies>
        <dependency>                            <!-- бібліотека для JSON -->
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
            <version>2.18.2</version>
        </dependency>
        <dependency>                            <!-- бібліотека для тестів -->
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.11.4</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

---

## `scope` — де потрібна залежність

| Scope | Значення | Приклад |
|---|---|---|
| `compile` | за замовчуванням: потрібна всюди | Jackson |
| `test` | лише в тестах, у готову програму не потрапить | JUnit |
| `runtime` | потрібна лише під час запуску | драйвер БД |
| `provided` | надасть сервер, ми не пакуємо | Servlet API |

<!-- element class="fragment" -->
На практиці 90 % часу: `compile` (нічого не писати) або `test`.

---

## Транзитивні залежності

Ми додали **одну** бібліотеку:

```text
jackson-databind 2.18.2
├── jackson-annotations 2.18.2
└── jackson-core 2.18.2
```

- Maven сам завантажив ще дві — це **транзитивні** залежності <!-- element class="fragment" -->
- Подивитись повне дерево: `mvn dependency:tree` <!-- element class="fragment" -->

<!-- element class="fragment" -->
Куди все завантажується? У локальну папку `~/.m2/repository` — **одну** на всі ваші проєкти.

---

## Основні команди

```bash
mvn compile            # скомпілювати
mvn test               # скомпілювати + запустити тести
mvn package            # скомпілювати + тести + зібрати .jar у target/
mvn clean              # видалити target/
mvn clean package      # зібрати з нуля

mvn dependency:tree    # дерево залежностей
```

```mermaid
flowchart LR
    A[compile] --> B[test] --> C[package] --> D[install]
```

Кожна команда виконує **всі попередні кроки**: `mvn package` спершу скомпілює і прожене тести.

note: install кладе ваш jar у локальний ~/.m2, щоб інші ваші проєкти могли його використати. deploy — у віддалене сховище компанії. На практиці в IntelliJ ці кнопки є у вкладці Maven справа.

---

## Конфлікт версій

```text
my-app
├── lib-a
│   └── commons-x 1.0      ← ближче до кореня
└── lib-b
    └── lib-c
        └── commons-x 2.0  ← далі
```

- Дві бібліотеки хочуть **різні** версії `commons-x`, а використати можна лише одну <!-- element class="fragment" -->
- Maven бере **найближчу** до вашого проєкту → `1.0` (не найновішу!) <!-- element class="fragment" -->
- Якщо `lib-c` потребує чогось із 2.0 — програма впаде **під час роботи** <!-- element class="fragment" -->

<!-- element class="fragment" -->
**Рішення:** явно вказати потрібну версію у своєму `pom.xml` — найближчою стане саме вона.

note: Правильніше — через <dependencyManagement> або BOM (scope import), це аналог Central Package Management у .NET. Для цієї групи достатньо ідеї "зафіксуй версію сам".

---

## Що комітити в Git

❌ **Не комітимо:**
- папку `target/` <!-- element class="fragment" -->
- `.jar`-файли бібліотек <!-- element class="fragment" -->

✅ **Комітимо:**
- `pom.xml` — цього достатньо, щоб будь-хто відновив усі залежності <!-- element class="fragment" -->
- `mvnw`, `mvnw.cmd`, `.mvn/` — Maven Wrapper: однакова версія Maven у всієї команди <!-- element class="fragment" -->

```text
# .gitignore
target/
```
<!-- element class="fragment" -->

---

## Ще кілька порад

- **Фіксуйте точні версії**: `2.18.2`, а не `LATEST` чи діапазони — інакше завтра збірка може поводитись інакше <!-- element class="fragment" -->
- **Не тягніть велику бібліотеку заради одного методу** <!-- element class="fragment" -->
- **Оновлюйте залежності**: у старих версіях бувають вразливості <!-- element class="fragment" -->

<!-- element class="fragment" -->
> Приклад: Log4Shell (2021) — критична дірка в бібліотеці логування `log4j`. Багато команд навіть не знали, що вона в них є: її підтягнула **транзитивно** інша бібліотека.

---

# Частина 7
## Gradle — одним слайдом

---

## Gradle

```kotlin
// build.gradle.kts — те саме, що наш pom.xml
plugins {
    java
}

dependencies {
    implementation("com.fasterxml.jackson.core:jackson-databind:2.18.2")
    testImplementation("org.junit.jupiter:junit-jupiter:5.11.4")
}
```

| | Maven | Gradle |
|---|---|---|
| Конфігурація | XML | Kotlin / Groovy код |
| Швидкість | нормальна | швидше (кешує, збирає лише змінене) |
| Конфлікт версій | найближча | найновіша |
| Де частіше | бекенд, enterprise | Android, великі проєкти |

Ідеї ті самі: координати, залежності, транзитивність.

---

## Підсумок

- **Анотація** — мітка з даними; сама нічого не робить. Не забувайте `@Retention(RUNTIME)` <!-- element class="fragment" -->
- **Reflection** — програма досліджує себе під час роботи: поля, методи, анотації <!-- element class="fragment" -->
- Рефлексія **повільна** — результати кешуємо, у гарячому коді не використовуємо <!-- element class="fragment" -->
- **Анотації + Reflection** = декларативний код: мітки окремо, логіка окремо <!-- element class="fragment" -->
- **Maven**: `pom.xml` описує залежності, Maven сам їх завантажує <!-- element class="fragment" -->
- У Git — `pom.xml`, а не `.jar` і не `target/` <!-- element class="fragment" -->

---

# Практика

---

## Задача 1. Дослідник класу

Напишіть метод `inspect(Class<?> type)`, який виводить:

- назву класу і пакет
- усі поля: тип і назву
- усі методи: тип результату, назву, кількість параметрів

Перевірте на власному класі `Student` і на `String.class`.

Питання: чому для `String` полів так мало, а методів так багато?

--

## Задача 1. Розв'язок

```java
static void inspect(Class<?> type) {
    IO.println("Клас: " + type.getSimpleName() + " (" + type.getPackageName() + ")");

    IO.println("Поля:");
    for (Field f : type.getDeclaredFields()) {
        IO.println("  " + f.getType().getSimpleName() + " " + f.getName());
    }

    IO.println("Методи:");
    for (Method m : type.getDeclaredMethods()) {
        IO.println("  " + m.getReturnType().getSimpleName() + " "
                + m.getName() + " (" + m.getParameterCount() + ")");
    }
}
```

---

## Задача 2. Знайдіть баг

```java
@Target(ElementType.METHOD)
public @interface Audit {
    String action();
}

class AccountService {
    @Audit(action = "withdraw")
    public void withdraw(long amount) { }
}

for (Method m : AccountService.class.getDeclaredMethods()) {
    if (m.isAnnotationPresent(Audit.class)) {
        IO.println("Аудит: " + m.getName());
    }
}
```

Що виведе програма? Чому? Як виправити?

--

## Задача 2. Розбір

- Програма **нічого не виведе** <!-- element class="fragment" -->
- Немає `@Retention` → за замовчуванням `CLASS` → рефлексія анотацію не бачить <!-- element class="fragment" -->
- Виправлення: додати `@Retention(RetentionPolicy.RUNTIME)` <!-- element class="fragment" -->

---

## Задача 3. `@Range`

1. Створіть анотацію `@Range(min, max)` для чисел
2. Додайте її перевірку в `ValidationEngine`
3. Перевірте:

```java
record Student(@MaxLength(30) String name,
               @Range(min = 0, max = 100) int grade) {}

ValidationEngine.validate(new Student("Anna", 150));
// grade: значення 150 поза межами [0; 100]
```

--

## Задача 3. Розв'язок

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.RECORD_COMPONENT)
public @interface Range {
    int min();
    int max();
}

// у циклі ValidationEngine, поруч із перевіркою MaxLength:
Range range = rc.getAnnotation(Range.class);
if (range != null && value instanceof Integer n) {
    if (n < range.min() || n > range.max()) {
        errors.add(rc.getName() + ": значення " + n + " поза межами ["
                + range.min() + "; " + range.max() + "]");
    }
}
```

note: invoke повертає Object, тому int приходить як Integer — це той самий boxing зі слайда про швидкість.

---

## Задача 4. Мінітестовий фреймворк

Напишіть `TestRunner.run(Class<?> testClass)`:

1. Створіть анотацію `@MyTest`
2. Знайдіть усі методи з нею
3. Для кожного: створіть об'єкт класу і викличте метод
4. Виняток → тест провалено
5. Виведіть: скільки пройдено, скільки провалено

--

## Задача 4. Розв'язок

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface MyTest {}

static void run(Class<?> testClass) throws ReflectiveOperationException {
    int passed = 0, failed = 0;

    for (Method m : testClass.getDeclaredMethods()) {
        if (!m.isAnnotationPresent(MyTest.class)) continue;

        Object instance = testClass.getDeclaredConstructor().newInstance();
        try {
            m.invoke(instance);
            IO.println("✓ " + m.getName());
            passed++;
        } catch (InvocationTargetException e) {
            IO.println("✗ " + m.getName() + ": " + e.getCause());
            failed++;
        }
    }
    IO.println("Пройдено: " + passed + ", провалено: " + failed);
}
```

Вітаю — ви щойно написали спрощений JUnit 🎉

---

## Задача 5. Перший Maven-проєкт

1. Створіть Maven-проєкт в IntelliJ IDEA
2. Підключіть Jackson (`jackson-databind`)
3. Перетворіть `record Student(String name, int grade)` у JSON і назад:

```java
ObjectMapper mapper = new ObjectMapper();
String json = mapper.writeValueAsString(new Student("Anna", 95));
Student back = mapper.readValue(json, Student.class);
```

4. Виконайте `mvn dependency:tree` — скільки бібліотек насправді завантажено?
5. Зберіть `.jar` через `mvn package` і знайдіть його в `target/`

note: Гарний місток до теми: Jackson усередині робить саме те, що ми робили на лекції, — рефлексією знаходить компоненти record і викликає канонічний конструктор.

---

# Питання?
