namespace Control;

public class Analyzer
{
    public int Count(int[][] rows, int threshold)
    {
        int hits = 0;
        foreach (var row in rows)
        {
            for (int i = 0; i < row.Length; i++)
            {
                if (row[i] > threshold)
                {
                    hits += 1;
                }
            }
        }
        return hits;
    }
}
