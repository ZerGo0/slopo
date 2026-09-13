## (9) score 0.98

Hash: `c9f4b3851218`

### ______ 1 ______

- `views/query_helpers.py` lines 358-373

```python
if sql:
```

```python
try:
    parameter_names = _derived_query_parameters(sql)
    params = {parameter: "" for parameter in parameter_names}
    analysis = await db.analyze_sql(sql, params)
    if _analysis_is_write(analysis):
        analysis_rows = await _analysis_rows_with_permissions(
            datasette, analysis, actor
        )
    else:
        analysis_error = (
            "Use /-/query for read-only SQL; "
            "this endpoint only executes writes"
        )
except (QueryValidationError, sqlite3.DatabaseError) as ex:
    analysis_error = getattr(ex, "message", str(ex))
```

### ______ 2 ______

- `views/execute_write.py` lines 256-272

```python
if sql and analysis_error is None:
```

```python
try:
    parameter_names = _derived_query_parameters(sql)
    if analysis is None:
        params = {parameter: "" for parameter in parameter_names}
        analysis = await db.analyze_sql(sql, params)
    if _analysis_is_write(analysis):
        analysis_rows = await _analysis_rows_with_permissions(
            self.ds, analysis, request.actor
        )
    else:
        analysis_error = (
            "Use /-/query for read-only SQL; "
            "this endpoint only executes writes"
        )
except (QueryValidationError, sqlite3.DatabaseError) as ex:
    analysis_error = getattr(ex, "message", str(ex))
```
