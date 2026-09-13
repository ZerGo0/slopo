## (7) score 0.97-1.00

Hash: `f3a306c88ec9`

### ______ 1 ______

- `java/com/github/benmanes/caffeine/cache/BoundedLocalCache.java` lines 3691-3701

- `java/com/github/benmanes/caffeine/cache/UnboundedLocalCache.java` lines 715-725

```java
@Override
public boolean retainAll(Collection<?> collection)
```

```java
{
  requireNonNull(collection);
  @Var boolean modified = false;
  for (K key : this) {
    if (!collection.contains(key) && remove(key)) {
      modified = true;
    }
  }
  return modified;
}
```

### ______ 2 ______

- `java/com/github/benmanes/caffeine/cache/BoundedLocalCache.java` lines 4100-4110

- `java/com/github/benmanes/caffeine/cache/LocalAsyncCache.java` lines 1638-1648

- `java/com/github/benmanes/caffeine/cache/UnboundedLocalCache.java` lines 1102-1112

```java
@Override
public boolean retainAll(Collection<?> collection)
```

```java
{
  requireNonNull(collection);
  @Var boolean modified = false;
  for (var entry : this) {
    if (!collection.contains(entry) && remove(entry)) {
      modified = true;
    }
  }
  return modified;
}
```
