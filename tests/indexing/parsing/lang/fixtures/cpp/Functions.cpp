int add(int a, int b) {
    return a + b;
}

struct Accumulator {
    int total;

    Accumulator(int start) : total(start) {}

    ~Accumulator() {
        total = 0;
    }

    void add_all(const std::vector<int> &values) {
        for (int value : values) {
            total += value;
        }
    }

    Accumulator &operator+=(int amount) {
        total += amount;
        return *this;
    }

    std::string describe() const;
};

double average(const std::vector<double> &values) {
    double sum = 0;
    for (double value : values) {
        sum += value;
    }
    return sum / values.size();
}

std::string Accumulator::describe() const {
    if (total == 0) {
        return "empty";
    }
    return "nonempty";
}
