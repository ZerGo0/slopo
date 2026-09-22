int allman(int a, int b)
{
    if (a > b)
    {
        return a;
    }
    return b;
}

int multi_line_signature(
    int first,
    int second
) {
    return first + second;
}

int multi_line_header(int a, int b, int c) {
    int total = 0;
    while (a > 0
        && b > 0
        && c > 0) {
        total += a;
        a -= 1;
    }
    return total;
}
