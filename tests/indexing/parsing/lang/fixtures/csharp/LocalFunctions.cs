namespace Text;

public class Formatter
{
    public string Indent(string[] lines, int spaces)
    {
        string Pad(string line) => new string(' ', spaces) + line;

        string head = Pad(lines[0]);
        string tail = Pad(lines[1]);
        return head + "\n" + tail;
    }
}
