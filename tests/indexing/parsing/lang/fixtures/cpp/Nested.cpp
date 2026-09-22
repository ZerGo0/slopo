int scan(const std::vector<int> &data) {
    int hits = 0;
    for (int value : data) {
        if (value > 0) {
            try {
                int remaining = probe(value);
                while (remaining > 0) {
                    hits++;
                    remaining -= 2;
                }
            } catch (const std::exception &e) {
                hits -= 1;
            }
        }
    }
    return hits;
}
