pub struct Grader {
    curve: i32,
}

impl Grader {
    pub fn classify(&self, score: i32) -> String {
        if score >= 90 {
            let bonus = self.curve / 2;
            return format!("A+{}", bonus);
        }

        if score >= 60 {
            String::from("pass")
        } else if score >= 40 {
            let note = score + self.curve;
            format!("borderline {}", note)
        } else {
            String::from("fail")
        }
    }

    pub fn adjust(&self, score: Option<i32>) -> i32 {
        if let Some(value) = score {
            let curved = value + self.curve;
            curved.min(100)
        } else {
            0
        }
    }
}
