namespace Control;

public class Router
{
    public string Route(int code)
    {
        switch (code)
        {
            case 1:
                string first = "home";
                return first;
            case 2:
            case 3:
                Log(code);
                return "section";
            default:
                return "not found";
        }
    }
}
