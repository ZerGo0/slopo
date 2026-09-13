class Exceptions {

    int parseOrZero(String text) {
        int value;
        try {
            value = Integer.parseInt(text);
            value = value * 2;
        } catch (NumberFormatException e) {
            value = 0;
            text = e.getMessage();
        } finally {
            text = text.trim();
            value = value + text.length();
        }
        return value;
    }

    int elementAt(int[] xs, int i, int fallback) {
        int result;
        try {
            result = xs[i];
            result = result + i;
        } catch (ArrayIndexOutOfBoundsException e) {
            result = fallback;
            fallback = fallback - 1;
        } catch (NullPointerException e) {
            result = 0;
        }
        return result;
    }

    String firstLine(Reader source) {
        String line = "";
        try (BufferedReader reader = new BufferedReader(source)) {
            line = reader.readLine();
            line = line.trim();
        } catch (IOException e) {
            line = "";
        }
        return line;
    }
}
