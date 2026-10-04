package lect11;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Random;
import java.util.function.BiFunction;
import java.util.function.Function;

public class Lect11 {
  static void main() {
//    var stringBox = new Box<String>();
//    stringBox.getFirst();
//    var o = stringBox.<Integer>mapToNewType();
//    var list = Arrays.asList(1, 2, 3, 4, 5);
//    var integers = List.of(1, 2, 3, 4, 5, 6);
//    integers.add(1);
    var aIntegerHashMap = new HashMap<A, Integer>();
    var a1 = new A(10);
    var a2 = new A(10);
    System.out.println(a1.equals(a2));
    aIntegerHashMap.put(a1, 10);
    aIntegerHashMap.put(a1, 15);
    System.out.println(aIntegerHashMap);
    DoSomething<Function<String, String>> b =
        (a)-> System.out.println(a.apply("Hello WOrlds"));
//    aIntegerHashMap.put()

  }

  @FunctionalInterface
  interface DoSomething<F extends Function>{
    void doSmth(F func);
  }

  static class A{
    public A(int value) {
      this.value = value;
    }

    private int value;

    @Override
    public boolean equals(Object o) {
      if (o == null || getClass() != o.getClass()) return false;
      A a = (A) o;
      return value == a.value;
    }

    @Override
    public int hashCode() {
      return new Random().nextInt();
    }
  }

  interface Repository<T, ID> {
    Optional<T> findById(ID id);
    List<T> findAll();
    void save(T entity);
  }

  class BoxRepository implements Repository<Box<Integer>, Integer>{

    @Override
    public Optional<Box<Integer>> findById(Integer integer) {
      return Optional.empty();
    }

    @Override
    public List<Box<Integer>> findAll() {
      return List.of();
    }

    @Override
    public void save(Box<Integer> entity) {

    }
  }
  static void print(StringList l)  { }
  static void print(IntegerList l) { }


  class StringList extends ArrayList<String>{}
  class IntegerList extends ArrayList<Integer>{}

  static class Box<MyType extends Number & Comparable<MyType>>{
    private List<MyType> myList = new ArrayList<>();

    public MyType getFirst(){
      return myList.getFirst();
    }

    public <NewType extends String> NewType mapToNewType(){
      return (NewType) String.valueOf(getFirst().doubleValue());

    }
  }

}
