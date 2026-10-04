package lect7and10;

public class Main {
  {
    System.out.println("Hello World");
  }


  static void main() {
    Integer a = 127, b = 127;
    Integer c = 128, d = 128;
    String s1 = new String("java"), s2 = new String("java");


//    System.out.println(a == b);
//    System.out.println(c == d);
//    System.out.println(a.equals(b));
//    System.out.println(c.equals(d));

//    System.out.print(s1.equals (s2));

//    Integer i = null;
//    if (i!=null){
//      Objects.equals(i, new Integer(1));
//      System.out.println(i.equals(new Integer(1)))
//    }
//    Scanner in = new Scanner(System.in);
//    Integer i = in.nextInt();
//    System.out.println(i);
//    in.close();
    boolean condition = true;
    int i = 10;
    switch (i){
      case 10: {
        System.out.println("case 10");
        break;
      }
      case 6: {
        System.out.println("case 6");
        break;
      }
      default: {
        System.out.println("default");
        break;
      }
    }
    var stringNumber = switch (i){
      case 10 -> {
        System.out.println(1231);
        yield "ten";
      }
      case 6 -> "six";
      default -> "default";
    };
//    System.out.println("else");
//    try(Scanner in = new Scanner(System.in)){
//      Integer i = in.nextInt();
//      System.out.println(i);
//    }

  }
}
