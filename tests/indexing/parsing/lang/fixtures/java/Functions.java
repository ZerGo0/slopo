public class Example {

    public static int add(int a, int b) {
        return a + b;
    }

    private String greet(String name) {
        return "Hello, " + name + "!";
    }

    public static double[] normalize(double[] values) {
        double sum = 0;
        for (double v : values) {
            sum += v;
        }
        double[] result = new double[values.length];
        for (int i = 0; i < values.length; i++) {
            result[i] = values[i] / sum;
        }
        return result;
    }

    @Deprecated
    public <T> List<T> repeat(T item, int times) {
        List<T> list = new ArrayList<>();
        for (int i = 0; i < times; i++) {
            list.add(item);
        }
        return list;
    }
}
