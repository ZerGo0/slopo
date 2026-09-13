namespace Style;

public class Mixed {
    public int KAndR(int a, int b) {
        if (a > b) {
            return a;
        }
        return b;
    }

    public int MultiLineSignature(
        int first,
        int second
    ) {
        return first + second;
    }

    public int MultiLineHeader(int a, int b, int c) {
        int total = 0;
        while (a > 0
            && b > 0
            && c > 0) {
            total += a;
            a -= 1;
        }
        return total;
    }
}
