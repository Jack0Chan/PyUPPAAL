package app;

class App {
  private static int OFF = 0;
  private static int ON = 1;
  static int state = OFF;

  public static void set_on() {
//    state = ON;
  }

  public static void set_off() {
    state = OFF;
  }

  public static void expect_on() {
    assert state==ON;
  }

  public static void expect_off() {
    assert state == OFF;
  }
}


