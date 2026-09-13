pub trait Shape {
    fn area(&self) -> f64;

    fn describe(&self) -> String {
        let area = self.area();
        format!("shape of {:.2}", area)
    }
}

pub struct Circle {
    radius: f64,
}

impl Shape for Circle {
    fn area(&self) -> f64 {
        std::f64::consts::PI * self.radius * self.radius
    }
}

pub async fn load_all(ids: &[u32]) -> Vec<Data> {
    let first = fetch(ids[0]).await;
    let rest = fetch_many(&ids[1..]).await;
    merge(first, rest)
}

pub mod geometry {
    pub fn diagonal(width: f64, height: f64) -> f64 {
        (width * width + height * height).sqrt()
    }
}
