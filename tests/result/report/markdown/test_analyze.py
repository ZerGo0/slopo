from datetime import datetime

from slopo.result.models import Cluster, HashedCluster, UnitRecord
from slopo.result.report.markdown.analyze import (
    build_cluster_analyze,
    build_index_analyze,
)


_UNITS = {
    1: UnitRecord(1, "src/A.java", "foo", 10, 20, "int foo() {}", "hashA"),
    2: UnitRecord(2, "src/B.java", "bar", 5, 15, "int bar() {}", "hashB"),
}
_CLUSTERS = [HashedCluster(Cluster([1, 2], 0.95, 0.97), "cluster-1-hash")]
_GENERATED_AT = datetime(2026, 6, 19, 14, 30, 0)


def test_renders_index_with_one_row_per_cluster():
    markdown = build_index_analyze(_CLUSTERS, _UNITS, _GENERATED_AT)

    assert (
        markdown
        == """\
Generated 2026-06-19 14:30:00

| Cluster                   | Hash           | Score     | Code units | Unique files |
|---------------------------|----------------|-----------|------------|--------------|
| [Cluster 1](cluster-1.md) | cluster-1-hash | 0.95-0.97 | 2          | 2            |
"""
    )


def test_index_counts_exact_duplicates_in_code_units_and_unique_files():
    units = {
        **_UNITS,
        3: UnitRecord(3, "src/C.java", "baz", 1, 11, "int foo() {}", "hashA"),
        4: UnitRecord(4, "src/A.java", "qux", 2, 12, "int foo() {}", "hashA"),
    }
    clusters = [HashedCluster(Cluster([1, 2, 3, 4], 0.95, 0.97), "dupes-hash")]

    markdown = build_index_analyze(clusters, units, _GENERATED_AT)

    assert (
        markdown
        == """\
Generated 2026-06-19 14:30:00

| Cluster                   | Hash       | Score     | Code units | Unique files |
|---------------------------|------------|-----------|------------|--------------|
| [Cluster 1](cluster-1.md) | dupes-hash | 0.95-0.97 | 4          | 3            |
"""
    )


def test_renders_cluster_with_each_unit_and_its_code_block():
    markdown = build_cluster_analyze(1, _CLUSTERS[0], _UNITS)

    assert (
        markdown
        == """\
## (1) score 0.95-0.97

Hash: `cluster-1-hash`

### ______ 1 ______

- `src/A.java` lines 10-20

```java
foo
```

```java
int foo() {}
```

### ______ 2 ______

- `src/B.java` lines 5-15

```java
bar
```

```java
int bar() {}
```
"""
    )


def test_svelte_script_uses_its_embedded_language():
    units = {
        1: UnitRecord(
            1,
            "src/Counter.svelte",
            "function amount(value: number)",
            2,
            4,
            "return value + 1",
            "script",
            "typescript",
        ),
    }
    cluster = HashedCluster(Cluster([1], 1.0, 1.0), "script-hash")

    markdown = build_cluster_analyze(1, cluster, units)

    assert "```typescript\nfunction amount(value: number)" in markdown
    assert "```typescript\nreturn value + 1" in markdown


def test_groups_exact_duplicates():
    units = {
        **_UNITS,
        3: UnitRecord(3, "src/C.java", "baz", 1, 11, "x", "hashA"),
    }
    cluster = Cluster([1, 3, 2], 0.95, 0.97)

    markdown = build_cluster_analyze(1, HashedCluster(cluster, "grouped-hash"), units)

    assert (
        markdown
        == """\
## (1) score 0.95-0.97

Hash: `grouped-hash`

### ______ 1 ______

- `src/A.java` lines 10-20

```java
foo
```

- `src/C.java` lines 1-11

```java
baz
```

```java
int foo() {}
```

### ______ 2 ______

- `src/B.java` lines 5-15

```java
bar
```

```java
int bar() {}
```
"""
    )


def test_orders_duplicates_by_file_path():
    units = {
        1: UnitRecord(1, "src/C.java", "foo", 10, 20, "int foo() {}", "hashA"),
        2: UnitRecord(2, "src/D.java", None, 1, 11, "x", "hashA"),
        3: UnitRecord(3, "src/A.java", "qux", 2, 12, "y", "hashA"),
    }
    cluster = Cluster([1, 2, 3], 0.95, 0.97)

    markdown = build_cluster_analyze(1, HashedCluster(cluster, "ordered-hash"), units)

    assert (
        markdown
        == """\
## (1) score 0.95-0.97

Hash: `ordered-hash`

### ______ 1 ______

- `src/A.java` lines 2-12

```java
qux
```

- `src/C.java` lines 10-20

```java
foo
```

- `src/D.java` lines 1-11

```java
int foo() {}
```
"""
    )


def test_renders_identical_context_once_before_the_body():
    units = {
        1: UnitRecord(1, "src/A.java", "foo", 10, 20, "int foo() {}", "hashA"),
        2: UnitRecord(2, "src/B.java", "foo", 30, 40, "int foo() {}", "hashA"),
    }
    cluster = Cluster([1, 2], 1.0, 1.0)

    markdown = build_cluster_analyze(1, HashedCluster(cluster, "grouped-hash"), units)

    assert (
        markdown
        == """\
## (1) score 1.00

Hash: `grouped-hash`

### ______ 1 ______

- `src/A.java` lines 10-20

- `src/B.java` lines 30-40

```java
foo
```

```java
int foo() {}
```
"""
    )


def test_groups_exact_copies_by_context():
    units = {
        1: UnitRecord(1, "src/A.java", "common", 10, 20, "body", "hashA"),
        2: UnitRecord(2, "src/B.java", "different", 30, 40, "body", "hashA"),
        3: UnitRecord(3, "src/C.java", "common", 50, 60, "body", "hashA"),
    }
    cluster = Cluster([1, 2, 3], 1.0, 1.0)

    markdown = build_cluster_analyze(1, HashedCluster(cluster, "grouped-hash"), units)

    assert (
        markdown
        == """\
## (1) score 1.00

Hash: `grouped-hash`

### ______ 1 ______

- `src/A.java` lines 10-20

- `src/C.java` lines 50-60

```java
common
```

- `src/B.java` lines 30-40

```java
different
```

```java
body
```
"""
    )
