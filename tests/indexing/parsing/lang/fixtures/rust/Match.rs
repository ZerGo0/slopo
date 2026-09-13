pub enum Event {
    Click { x: i32, y: i32 },
    Key(char),
    Scroll(i32),
    Close,
}

pub fn handle(event: Event, state: i32) -> i32 {
    match event {
        Event::Click { x, y } => {
            let distance = x * x + y * y;
            state + distance
        }
        Event::Key(c) if c.is_ascii_digit() => state + c as i32,
        Event::Scroll(delta) => match delta.signum() {
            1 => state + delta,
            -1 => state - delta,
            _ => state,
        },
        Event::Close => 0,
    }
}
