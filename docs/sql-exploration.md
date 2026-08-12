# SQL exploration notes (Stage 4)

These queries were run against the local PostgreSQL `tasks` database.

## List every task

```sql
SELECT * FROM tasks ORDER BY id;
```

| id | title | done |
|---:|---|---|
| 1 | Buy groceries | false |
| 2 | Write documentation | true |
| 3 | Review pull request | false |

## Show only completed tasks

```sql
SELECT * FROM tasks WHERE done = true;
```

## Count all tasks

```sql
SELECT COUNT(*) FROM tasks;
```

## Mark every task as completed

```sql
UPDATE tasks SET done = true;
```

## Delete all completed tasks

```sql
DELETE FROM tasks WHERE done = true;
```

After changing rows directly in the database, `GET /tasks` immediately
reflects those changes because the API reads from PostgreSQL on every request.

## Optional extras used by the API

```sql
SELECT * FROM tasks WHERE done = true ORDER BY id;

SELECT * FROM tasks WHERE title ILIKE '%doc%' ORDER BY id;

SELECT
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE done = true) AS done,
  COUNT(*) FILTER (WHERE done = false) AS pending
FROM tasks;
```
