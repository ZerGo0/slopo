namespace Control;

public class Grader
{
    public string Classify(int score)
    {
        if (score >= 90)
        {
            return "A";
        }

        if (score >= 60)
        {
            return "pass";
        }
        else
        {
            string note = "retake recommended";
            return note;
        }
    }
}
