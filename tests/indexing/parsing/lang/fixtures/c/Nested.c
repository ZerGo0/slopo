int scan(const int *data, int count) {
    int hits = 0;
    for (int i = 0; i < count; i++) {
        if (data[i] > 0) {
            int remaining = data[i];
            while (remaining > 0) {
                hits++;
                remaining -= 2;
            }
        }
    }
    return hits;
}
