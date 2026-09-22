int guard(int *p) {
    if (p == 0)
        return -1;
    *p += 1;
    return *p;
}

int product(const int *values, int count) {
    int result = 1;
    for (int i = 0; i < count; i++)
        result *= values[i];
    return result;
}
