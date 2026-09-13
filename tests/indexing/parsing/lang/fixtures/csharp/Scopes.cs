using System;

namespace Control;

public class Writer
{
    private readonly object _gate = new object();

    public void Persist(string path, string data)
    {
        using (var stream = Open(path))
        {
            stream.Write(data);
            stream.Flush();
        }

        lock (_gate)
        {
            _pending += 1;
            Commit();
        }
    }
}
