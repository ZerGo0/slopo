namespace Geometry;

public class Rectangle
{
    private readonly double _width;
    private readonly double _height;

    public Rectangle(double width, double height)
    {
        _width = width;
        _height = height;
    }

    public double Area()
    {
        return _width * _height;
    }

    public double Scale(double factor)
    {
        double w = _width * factor;
        double h = _height * factor;
        return w * h;
    }

    public override string ToString() => $"Rectangle({_width}x{_height})";
}
