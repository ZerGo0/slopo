## (2) score 1.03

Hash: `4d65df1c5892`

### ______ 1 ______

- `java/com/github/benmanes/caffeine/cache/Policy.java` lines 380-385

- `java/com/github/benmanes/caffeine/cache/Policy.java` lines 820-825

```java
default Optional<Duration> ageOf(K key)
```

```java
{
  OptionalLong duration = ageOf(key, TimeUnit.NANOSECONDS);
  return duration.isPresent()
      ? Optional.of(Duration.ofNanos(duration.getAsLong()))
      : Optional.empty();
}
```
