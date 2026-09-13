namespace Control;

public class Aggregator
{
    public int Run(int[] values, int limit)
    {
        int total = 0;
        int steps = 0;

        for (int i = 0; i < values.Length; i++)
        {
            int value = values[i];
            total += value * i;
            steps += 1;
        }

        foreach (var value in values)
        {
            int weighted = value * 3;
            total += weighted - steps;
        }

        while (total > limit)
        {
            total -= limit;
            total = total / 2;
        }

        do
        {
            total += steps;
        } while (total < limit);

        return total;
    }
}
