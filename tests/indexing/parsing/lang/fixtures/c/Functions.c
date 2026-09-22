int add(int a, int b) {
    return a + b;
}

const char *pick(const char *primary, const char *fallback) {
    if (primary != 0) {
        return primary;
    }
    return fallback;
}

double average(const double *values, int count) {
    double sum = 0;
    for (int i = 0; i < count; i++) {
        sum += values[i];
    }
    return sum / count;
}

void clamp_in_place(int *value, int lo, int hi) {
    if (*value < lo) {
        *value = lo;
        return;
    }
    if (*value > hi) {
        *value = hi;
    }
}
