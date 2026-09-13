class Formatting {

    String tier(int score)
    {
        String label;
        if (score >= 90)
        {
            label = "gold";
            score -= 90;
        }
        else if (score >= 50)
        {
            label = "silver";
        }
        else
        {
            label = "bronze";
            score = 0;
        }
        return label;
    }

    long product(
            int[] factors,
            int start
    ) {
        long total = 1;
        for (int i = start;
                i < factors.length;
                i++) {
            total *= factors[i];
        }
        return total;
    }

    int readValue(BufferedReader source, int fallback)
    {
        int value;
        try (
                BufferedReader reader = source;
                Closeable guard = source
        ) {
            value = Integer.parseInt(reader.readLine());
            value = value * 2;
        }
        catch (IOException
                | NumberFormatException e)
        {
            value = fallback;
        }
        return value;
    }
}
