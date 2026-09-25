int classify(int n) {
    int score = 0;
    if (n < 0) {
        score = -n;
        score += 1;
        return score;
    }
    if (n == 0) {
        score = 100;
        score /= 2;
    } else {
        score = n * 3;
        score -= 4;
    }
    return score;
}

const char *grade(int marks, int bonus) {
    if (marks + bonus >= 90) {
        int total = marks + bonus;
        return total > 95 ? "A+" : "A";
    } else if (marks >= 50) {
        int deficit = 70 - marks;
        return deficit > 0 ? "C" : "B";
    } else {
        return "F";
    }
}
