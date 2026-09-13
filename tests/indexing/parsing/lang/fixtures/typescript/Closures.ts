function setup(worker: Worker): number[] {
  const doubler = function (x: number): number {
    const scaled = x * 2;
    return scaled;
  };

  worker.onComplete = (): void => {
    log("done");
    log("really done");
  };

  const config = {
    reset: (): void => {
      worker.value = 0;
    },
  };

  return items.map((v: number): number => {
    const scaled = doubler(v);
    return scaled + 1;
  });
}
