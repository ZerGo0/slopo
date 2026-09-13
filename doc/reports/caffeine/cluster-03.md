## (3) score 1.03

Hash: `216ec946cb7e`

### ______ 1 ______

- `java/com/github/benmanes/caffeine/cache/LocalAsyncCache.java` lines 485-492

```java
@SuppressWarnings({"CheckReturnValue", "FutureReturnValueIgnored"})
@Override public void replaceAll(BiFunction<? super K, ? super CompletableFuture<V>,
    ? extends CompletableFuture<V>> function)
```

```java
{
  requireNonNull(function);
  for (K key : keySet()) {
    computeIfPresent(key, (k, oldValue) -> requireNonNull(function.apply(k, oldValue)));
  }
}
```

### ______ 2 ______

- `java/com/github/benmanes/caffeine/cache/LocalAsyncCache.java` lines 980-988

```java
@Override
@SuppressWarnings("ResultOfMethodCallIgnored")
public void replaceAll(BiFunction<? super K, ? super V, ? extends V> function)
```

```java
{
  requireNonNull(function);
  for (K key : keySet()) {
    computeIfPresent(key, (k, oldValue) ->
        requireNonNull(function.apply(k, oldValue)),                   false);
  }
}
```
