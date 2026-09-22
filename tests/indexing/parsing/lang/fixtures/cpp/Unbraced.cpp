int guard(int *p) {
    if (p == nullptr)
        return -1;
    *p += 1;
    *p *= 2;
    return *p;
}

int product(const std::vector<int> &values) {
    int result = 1;
    for (int value : values)
        result *= value;
    result -= 1;
    return result;
}
