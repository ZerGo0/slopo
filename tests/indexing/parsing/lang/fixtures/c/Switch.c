int describe(int code, int *out) {
    int handled = 1;
    switch (code) {
        case 0:
            *out = code;
            *out += 10;
            break;
        case 1:
        case 2:
            *out = code * 2;
            break;
        case 3: {
            int scaled = code * code;
            *out = scaled - 1;
            break;
        }
        default:
            handled = 0;
    }
    return handled;
}
