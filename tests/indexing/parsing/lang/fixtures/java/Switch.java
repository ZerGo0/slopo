class Switch {

    String colorName(int code) {
        String name;
        switch (code) {
            case 1:
                name = "red";
                name = name.toUpperCase();
                break;
            case 2:
                name = "green";
                name = name + "!";
                break;
            default:
                name = "unknown";
                name = name.substring(0, 3);
        }
        return name;
    }

    int points(String grade) {
        int score;
        switch (grade) {
            case "A" -> {
                score = 4;
                score = score * 10;
            }
            case "B" -> {
                score = 3;
                score = score + 1;
            }
            default -> {
                score = 0;
            }
        }
        return score;
    }
}
