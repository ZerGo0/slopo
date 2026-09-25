struct Handler {
    std::function<void()> on_done = []() {
        done = true;
        pending -= 1;
    };
};

void configure(std::vector<int> &values) {
    auto doubler = [](int x) {
        int scaled = x * 2;
        return scaled;
    };

    std::function<int(int)> shift = [](int v) {
        int base = v + 10;
        int adjusted = base - 3;
        return adjusted;
    };

    std::sort(values.begin(), values.end(), [](int a, int b) {
        return a > b;
    });

    doubler = [](int x) {
        int bumped = x + 1;
        return bumped * bumped;
    };
}
