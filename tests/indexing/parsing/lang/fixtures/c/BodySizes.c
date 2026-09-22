int forward_declared(int a);

int empty_body(void) {}

int accumulate(const int *items, int count, int limit) {
    int result = 0;
    for (int i = 0; i < count; i++) {
        if (result >= limit) {
            break;
        }
        result += items[i];
    }
    return result;
}
