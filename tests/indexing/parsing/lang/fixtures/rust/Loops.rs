pub fn scan(rows: &[Vec<i32>], limit: i32) -> i32 {
    let mut total = 0;

    for row in rows {
        let head = row[0];
        total += head * 2;
    }

    while total > limit {
        total -= limit;
        total /= 2;
    }

    let mut stack = vec![total, limit];
    while let Some(top) = stack.pop() {
        total += top;
    }

    loop {
        total += 1;
        if total % 7 == 0 {
            break;
        }
    }

    let capped = 'search: loop {
        let next = total * 2;
        if next > limit {
            break 'search limit;
        }
        total = next;
    };

    total + capped
}
