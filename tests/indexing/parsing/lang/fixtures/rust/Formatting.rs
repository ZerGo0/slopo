pub fn within<'a, T>(
    items: &'a [T],
    lower: &T,
    upper: &T,
) -> Vec<&'a T>
where
    T: PartialOrd,
{
    let mut kept = Vec::new();
    for item in items {
        if item >= lower
            && item <= upper
        {
            kept.push(item);
        }
    }
    kept
}

pub fn describe(kind: &Kind) -> &'static str {
    match kind {
        Kind::Alpha
        | Kind::Beta
        | Kind::Gamma => "early",
        Kind::Delta if kind.is_late() => {
            "late delta"
        }
        _ => "other",
    }
}
