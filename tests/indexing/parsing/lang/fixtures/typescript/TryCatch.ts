function process(payload: string): Result {
  let result = null;
  try {
    result = parse(payload);
    result.validate();
  } catch (err) {
    log(err);
    result = fallback();
  } finally {
    cleanup();
    release();
  }
  return result;
}
