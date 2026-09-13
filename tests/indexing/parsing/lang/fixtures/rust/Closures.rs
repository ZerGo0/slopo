struct Worker {
    on_complete: Box<dyn Fn()>,
}

pub fn run(values: &[i32], factor: i32) -> Vec<i32> {
    let doubler = |x: i32| x * factor;

    let mut seen = 0;
    let mut record = move |x: i32| {
        seen += x;
        seen
    };

    let mut worker = Worker {
        on_complete: Box::new(|| {}),
    };
    worker.on_complete = || {
        println!("done");
    };

    let refresh = async move {
        let fresh = fetch(factor).await;
        cache(fresh);
    };
    spawn(refresh);

    values
        .iter()
        .map(|v| {
            let scaled = doubler(*v);
            scaled + record(scaled)
        })
        .filter(|v| *v > 0)
        .collect()
}
