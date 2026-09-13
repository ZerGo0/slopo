pub fn empty_body() {}

pub fn with_logic(numbers: &[i32]) -> i32 {
    let mut total = 0;
    for n in numbers {
        if n % 2 == 0 {
            total += n;
        } else {
            total -= n;
        }
    }
    total
}
