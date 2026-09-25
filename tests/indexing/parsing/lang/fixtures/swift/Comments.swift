// Overview of the module.
import Foundation

/// Normalizes readings against a calibration offset.
/// Returns a magnitude, never a negative value.
func normalize(readings: [Int], offset: Int) -> Int {
    // start from a clean total
    var total = 0

    for value in readings {
        total += value - offset /* remove the bias */
    }

    /*
      Fold a negative result back to a magnitude so
      callers can treat the output uniformly.
    */
    if total < 0 {
        total = -total
    }

    let note = "sep // not a comment /* still text */"
    return total + note.count
}
