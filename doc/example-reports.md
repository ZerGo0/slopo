# Example reports from real projects

Only a few clusters were retained from the original report for demonstrating purposes. All projects are small, so you can quickly generate complete reports yourself.

## Caffeine (Java)

- [cluster-01.md](reports/caffeine/cluster-01.md) - Two similar distant functions within a large file with different signatures. The function signature is separated from the body because only the body is compared. Signature is a context for readability only.
- [cluster-02.md](reports/caffeine/cluster-02.md) - Two exact copies with identical signatures in the same file.
- [cluster-03.md](reports/caffeine/cluster-03.md) - Two similar functions with different signatures.
- [cluster-07.md](reports/caffeine/cluster-07.md) - Mix of exact copies and similar functions across different files. Two similar variants, each having exact copies.
- [cluster-09.md](reports/caffeine/cluster-09.md) - Function body similar to code block inside conditional.
- [cluster-10.md](reports/caffeine/cluster-10.md) - Two exact copies, but each has a different signature.

The report contains code snippets from https://github.com/ben-manes/caffeine on the [Apache-2.0 license](https://github.com/ben-manes/caffeine?tab=Apache-2.0-1-ov-file)

Slopo configuration

```yaml
source_dir: caffeine/src/main
```

## Datasette (Python)

- [cluster-01.md](reports/datasette/cluster-01.md) - Two exact copies from distant files give the highest score. The function signature is separated from the body, and only the body is included in the comparison.
- [cluster-04.md](reports/datasette/cluster-04.md) - Two exact copies within almost identical conditional expressions.
- [cluster-09.md](reports/datasette/cluster-09.md) - Two similar blocks of code within different conditional expressions.

The report contains code snippets from https://github.com/simonw/datasette on the [Apache-2.0 license](https://github.com/simonw/datasette?tab=Apache-2.0-1-ov-file)

Slopo configuration

```yaml
source_dir: datasette
source_dir_exclude:
  - "**/static/**"
```
