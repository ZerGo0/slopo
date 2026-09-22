/// Documentation
/// spanning lines
int with_comments(int a, int b) {
    // a leading line comment
    int sum = a + b; // a trailing line comment
    /* a block comment
       spanning lines */
    std::string url = "http://not-a-comment";

    switch (code) {
        case 1:
            prepare();
            // a comment between statements
            dispatch();
    }

    return sum;
}
