class Animal:
    def __init__(self, name:str, age, color):
        self.__name = name
        self.__age = age
        self.__color = color

    def speak(self):
        print("Animal Speaking")
    @staticmethod
    def staticMethod():
        pass

    @property
    def name(self):
        return self.__name
    @name.setter
    def name(self, n):
        if(not isinstance(n, str)):
            raise TypeError("name must be a string")
        self.__name = n

animal = Animal("name", 12, "blue")
animal.name = "newName"
class Dog(Animal):
    counter = 0

    def __init__(self, name, age, color=None, breed=None, *args, **kwargs):
        super().__init__(name, age, color)
        self.breed = breed
        Dog.counter = Dog.counter + 1

    def __add__(self, other):
        return Dog(self._name + other._name, self._age, other._name)

    def __int__(self):
        return self._age

    def __repr__(self):
        return f"Dog({self._name}, {self._age}, {self.color})"



    def __getitem__(self, item: int):
        if (item == 2):
            return self._age
        elif (item == 3):
            return self.breed
        else:
            raise IndexError("hello")
    def __call__(self, *args, **kwargs):
        print(args, kwargs)

    def speak(self):
        super().speak()
        self.bark()

    def bark(self):
        print(Dog.counter)



#
# dog = Dog("Rex", 12, "taxa", " ", " ", " ", " ", " ")
# dog = Dog("Rex", 12, "taxa", " ", " ", " ", " ", " ")
# dog = Dog("Rex", 12, "taxa", " ", " ", " ", " ", " ")
# my_favourite_dog = Dog("NeRex", 12, "taxa", " ", " ", " ", " ", " ")
#
# favourite_dog = dog + my_favourite_dog

# print(favourite_dog)
# dog.bark()
# print(dog[dog])
# Dog.bark(dog)


# name = dog.__age
# print(name)

list = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]


if("d" in list):
    print(list)

def add_two_numbers(a: int, b: int) -> int:
    return a + b

# dog("Hello", "doggy", name="rex")
Dog("dasd","dasd","dasda","dasd")("dasda","Dasda")

def repeat(f):
    def wrapper(*args, **kwargs):
        print("repeat")
        f(*args, **kwargs)
        f(*args, **kwargs)

    return wrapper


@repeat
def hello():
    print("hello")



if __name__ == "__main__":
    hello()