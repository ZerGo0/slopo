using System;

namespace Control;

public class Loader
{
    public string Read(string path)
    {
        try
        {
            string raw = Fetch(path);
            return raw.Trim();
        }
        catch (FileNotFoundException e)
        {
            Log(e);
            return "";
        }
        catch (IOException e) when (e.InnerException != null)
        {
            Log(e.InnerException);
            throw;
        }
        finally
        {
            Cleanup();
        }
    }
}
