## (9) score 0.95-1.00

Hash: `eb4536942bb0`

### ______ 1 ______

- `java/com/github/benmanes/caffeine/cache/BoundedLocalCache.java` lines 419-438

- `java/com/github/benmanes/caffeine/cache/UnboundedLocalCache.java` lines 186-205

```java
@Override
public void notifyRemoval(@Nullable K key, @Nullable V value, RemovalCause cause)
```

```java
{
  var removalListener = removalListener();
  if (removalListener == null) {
    return;
  }
  Runnable task = () -> {
    try {
      removalListener.onRemoval(key, value, cause);
    } catch (Throwable t) {
      logger.log(Level.WARNING, "Exception thrown by removal listener", t);
    }
  };
  try {
    executor.execute(task);
  } catch (Throwable t) {
    logger.log(Level.ERROR, "Exception thrown when submitting removal listener", t);
    task.run();
  }
}
```

### ______ 2 ______

- `java/com/github/benmanes/caffeine/cache/Async.java` lines 94-108

```java
if (value != null)
```

```java
{
  Runnable task = () -> {
    try {
      delegate.onRemoval(key, value, cause);
    } catch (Throwable t) {
      logger.log(Level.WARNING, "Exception thrown by removal listener", t);
    }
  };
  try {
    executor.execute(task);
  } catch (Throwable t) {
    logger.log(Level.ERROR, "Exception thrown when submitting removal listener", t);
    task.run();
  }
}
```
