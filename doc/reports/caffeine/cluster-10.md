## (10) score 1.00

Hash: `e51ce08f7c2d`

### ______ 1 ______

- `java/com/github/benmanes/caffeine/cache/LocalAsyncLoadingCache.java` lines 189-199

```java
@Override
public CompletableFuture<Map<K, V>> refreshAll(Iterable<? extends K> keys)
```

- `java/com/github/benmanes/caffeine/cache/LocalLoadingCache.java` lines 185-195

```java
@Override
default CompletableFuture<Map<K, V>> refreshAll(Iterable<? extends K> keys)
```

```java
{
  var result = new LinkedHashMap<K, CompletableFuture<V>>(
      calculateHashMapCapacity(keys));
  for (K key : keys) {
    result.computeIfAbsent(key, this::refresh);
  }
  @SuppressWarnings("NullAway")
  Map<K, CompletableFuture<@Nullable V>> futures = result;
  return composeResult(futures);
}
```
