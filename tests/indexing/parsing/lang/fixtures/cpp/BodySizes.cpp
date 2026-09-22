int forward_declared(int a);

int empty_body() {}

int accumulate(const std::vector<int> &items, int limit) {
    int result = 0;
    for (int value : items) {
        if (result >= limit) {
            break;
        }
        result += value;
    }
    return result;
}
