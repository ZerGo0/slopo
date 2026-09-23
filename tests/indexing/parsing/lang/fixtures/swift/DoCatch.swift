func run(inputs: [Int]) -> Int {
    var total = 0

    do {
        let parsed = try parse(inputs)
        total += parsed
    } catch let error as FormatError {
        total = error.code
    } catch let error {
        log(error)
        total = -1
    }

    do {
        total += try compute(total)
    } catch {
        total = 0
    }
    return total
}
