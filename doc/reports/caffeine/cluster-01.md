## (1) score 1.04

Hash: `a5b5d09b0885`

### ______ 1 ______

- `java/com/github/benmanes/caffeine/cache/BoundedLocalCache.java` lines 384-393

```java
@Override
public boolean isPendingEviction(K key)
```

```java
{
  Node<K, V> node = data.get(nodeFactory.newLookupKey(key));
  if (node == null) {
    return false;
  }
  boolean expired = hasExpired(node, expirationTicker().read());
  V value = node.getValue();
  return (value == null) || (expired && !isComputingAsync(value));
}
```

### ______ 2 ______

- `java/com/github/benmanes/caffeine/cache/BoundedLocalCache.java` lines 2296-2311

```java
@Override
public boolean containsKey(@Nullable Object key)
```

```java
{
  requireNonNull(key);

  Node<K, V> node = data.get(nodeFactory.newLookupKey(key));
  if (node == null) {
    return false;
  }
  boolean expired = hasExpired(node, expirationTicker().read());
  V value = node.getValue();
  if ((value == null) || (expired && !isComputingAsync(value))) {
    scheduleDrainBuffers();
    return false;
  }
  return true;
}
```
