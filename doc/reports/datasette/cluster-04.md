## (4) score 1.00

Hash: `9a25c60e3ec4`

### ______ 1 ______

- `views/row.py` lines 390-403

```python
if self.ds.cache_headers and response.status == 200:
```

- `views/table.py` lines 1719-1732

```python
if datasette.cache_headers and response.status == 200:
```

```python
if private:



    response.headers["Cache-Control"] = "private, no-store"
    response.headers["Vary"] = "Cookie"
else:
    ttl = int(ttl)
    if ttl == 0:
        ttl_header = "no-cache"
    else:
        ttl_header = f"max-age={ttl}"
    response.headers["Cache-Control"] = ttl_header
```
