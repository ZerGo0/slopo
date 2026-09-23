func scan(rows: [[Int]], limit: Int) -> Int {
    var hits = 0
    for row in rows {
        if row.count > limit {
            for cell in row {
                switch cell.signum() {
                case 1:
                    hits += cell
                default:
                    hits -= 1
                }
            }
        }
    }
    return hits
}
