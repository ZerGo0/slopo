long sum_positive(const int *values, int count) {
    long total = 0;
    for (int i = 0; i < count; i++) {
        int v = values[i];
        total += v;
        total *= 2;
    }
    {
        long adjustment = count * 2;
        total -= adjustment;
    }
    return total;
}

int collatz_steps(int n) {
    int steps = 0;
    while (n > 1) {
        n = n % 2 == 0 ? n / 2 : 3 * n + 1;
        steps++;
    }
    return steps;
}

int last_before_zero(const int *cursor) {
    int last = 0;
    do {
        last = *cursor;
        cursor++;
    } while (last != 0);
    return last;
}
