# Select rows based on function name

```
SELECT
       f2.name,
       v.value,
       v2.value as returnval,
       f3.name as `calling_filename`,
       f4.name as `definition_filename`,
       f.linenum
FROM
     function_invocations f
       LEFT JOIN function_names f2 ON f.name = f2.rowid
       LEFT JOIN file_names f3 on f.calling_filename = f3.rowid
       LEFT JOIN file_names f4 on f.definition_filename = f4.rowid
       LEFT JOIN invocation_parameters parameter on f.hash = parameter.function_invocation_hash
       LEFT JOIN "values" v on parameter.value_id = v.rowid
       LEFT JOIN "values" v2 on f.returnval = v2.ROWID
WHERE f.name =
      (SELECT f4.rowid
       FROM function_names f4
       WHERE
           f4.name = 'explode');
```

# Select rows based on function name _and_ definition file name

SELECT
  f2.name,
  f.params,
  f.returnval,
  f3.name as `calling_filename`,
  f4.name as `definition_filename`,
  f.linenum
FROM
  function_calls f
    LEFT JOIN function_names f2 ON f.name = f2.rowid
    LEFT JOIN file_names f3 on f.calling_filename = f3.rowid
    LEFT JOIN file_names f4 on f.definition_filename = f4.rowid
WHERE f.name =
      (SELECT f4.rowid
       FROM function_names f4
       WHERE
         f4.name = 'saveData')
AND f4.name LIKE '%46652%';
