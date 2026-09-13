class Nesting {

    int process(int[] xs, int threshold) {
        int total = 0;
        for (int x : xs) {
            if (x > threshold) {
                try {
                    total = total + 100 / x;
                } catch (ArithmeticException e) {
                    total = total - 1;
                }
            }
        }
        return total;
    }
}
