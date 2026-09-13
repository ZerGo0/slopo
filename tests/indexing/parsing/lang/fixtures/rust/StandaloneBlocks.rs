pub fn totals(rows: &[Row], raw: *const u8) -> i64 {
    let gross = {
        let mut sum = 0;
        for row in rows {
            sum += row.amount;
        }
        sum
    };

    unsafe {
        let first = *raw;
        record(first);
    }

    let Some(rate) = lookup() else {
        let fallback = gross / 2;
        record(fallback as u8);
        return fallback;
    };

    {
        let scaled = gross * rate;
        record(scaled as u8);
    }

    gross
}
