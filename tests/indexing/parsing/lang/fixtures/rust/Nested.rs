pub fn count(rows: &[Vec<i32>], threshold: i32) -> usize {
    let mut hits = 0;
    for row in rows {
        for cell in row {
            if *cell > threshold {
                hits += 1;
            }
        }
    }
    hits
}
