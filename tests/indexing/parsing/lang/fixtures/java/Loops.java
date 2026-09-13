class Loops {

    String join(String[] parts) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < parts.length; i++) {
            out.append(parts[i]);
            out.append(",");
        }
        return out.toString();
    }

    int largest(int[] xs) {
        int max = xs[0];
        for (int x : xs) {
            max = x > max ? x : max;
        }
        return max;
    }

    long fib(int n) {
        long a = 0;
        long b = 1;
        while (n > 0) {
            long next = a + b;
            a = b;
            b = next;
            n = n - 1;
        }
        return a;
    }

    int digits(int n) {
        int count = 0;
        do {
            n = n / 10;
            count = count + 1;
        } while (n != 0);
        return count;
    }
}
