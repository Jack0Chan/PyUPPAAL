package app;

/** Correct implementation: maximum level is 10 */
class App
{
    private static int OFF = 0;
    private static int ON = 1;
    static int state = OFF;

    public static void up() {
        state++;
    }

    public static void down() {
        state--;
    }

    public static void expect_max() {
        assert state == 10;
    }

    public static void expect_on(int val) {
        assert state == val;
    }

    public static void expect_off() {
        assert state == 0;
    }
}
