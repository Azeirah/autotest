# Select rows based on function name

```sql
SELECT
  f2.name,
  v.value as parameter,
  v2.value as returnval,
  f3.name as `calling_filename`,
  f4.name as `definition_filename`,
  f.linenum
FROM
 function_invocations f
   LEFT JOIN function_names f2 ON f.name = f2.rowid
   LEFT JOIN file_names f3 on f.calling_filename = f3.rowid
   LEFT JOIN file_names f4 on f.definition_filename = f4.rowid
   -- the cast is only necessary for older db versions, where I accidentally stored the funtion_invocation.hash as an INTEGER affinity
   -- it can be left out in newer versions
   LEFT JOIN invocation_parameters parameter on parameter.function_invocation_hash = cast(f.hash as text)
   LEFT JOIN "values" v on parameter.value_id = v.rowid
   LEFT JOIN "values" v2 on f.returnval = v2.ROWID
WHERE f.name =
  (SELECT f4.rowid
   FROM function_names f4
   WHERE
       f4.name = 'explode');
  --             ^^^^^^^^^
  -- specify your desired function name here
```