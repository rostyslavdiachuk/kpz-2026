package lect7and10;

public class Main2 {
  static void main() {

  }

  record Pair<A, B>(A first, B second) {
  }

  static String describe(Pair<Object, Object> pair) {
    return switch (pair) {
      case Pair(String a, String b) -> "Два рядки: " + a + b;
      case Pair(Integer a, Integer b) -> "Сума: " + (a + b);
      case Pair(var a, var b) when a == null || b == null -> "Є null";
      case Pair(var _, var _) -> "Змішана пара";
    };
  }



//  public sealed class Shape permits Circle, Square, Rectangle { }
//
//  public record Circle(double radius) extends Shape{}
//
//  public final class Circle extends Shape {
//    final double radius;
//    Circle(double radius) { this.radius = radius; }
//  }
//
//  public record Square(double side) extends Shape{}
//  public final class Square extends Shape {
//    final double side;
//    Square(double side) { this.side = side; }
//  }

//  public non-sealed class Rectangle extends Shape {
//    final double w, h;
//    Rectangle(double w, double h) { this.w = w; this.h = h; }
//  }
//
//  public final class Paralelogram extends Rectangle{
//
//    Paralelogram(double w, double h) {
//      super(w, h);
//    }
//  }


}
