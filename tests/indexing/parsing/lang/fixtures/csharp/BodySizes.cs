using System;

namespace Shapes;

public interface IShape
{
    double Area();
}

public class Circle
{
    public void Reset()
    {
    }

    public double Radius() => _radius;

    public double Diameter()
    {
        double radius = 2.0;
        double diameter = radius * 2;
        if (diameter < 0)
        {
            throw new InvalidOperationException("negative diameter");
        }
        return diameter;
    }
}
