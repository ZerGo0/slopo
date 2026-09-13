class Conditionals {

    String describe(int score) {
        String tier;
        if (score >= 90) {
            tier = "gold";
            score = score - 90;
        } else if (score >= 50) {
            tier = "silver";
        } else {
            tier = "bronze";
            score = 0;
        }
        return tier + ":" + score;
    }

    int settle(int value, int min, int max) {
        int adjusted = value;
        if (value < min) {
            int deficit = min - value;
            adjusted = min + deficit / 2;
        }
        if (value > max) {
            adjusted = max;
            return adjusted - 1;
        }
        return adjusted;
    }
}
