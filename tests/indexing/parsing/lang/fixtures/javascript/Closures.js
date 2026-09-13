function setup(worker) {
  const doubler = function (x) {
    const scaled = x * 2;
    return scaled;
  };

  worker.onComplete = () => {
    log("done");
    log("really done");
  };

  const config = {
    reset: () => {
      worker.value = 0;
    },
  };

  return items.map((v) => {
    const scaled = doubler(v);
    return scaled + 1;
  });
}
