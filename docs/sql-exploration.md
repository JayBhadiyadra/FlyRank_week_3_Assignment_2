# SQL exploration notes (Stage 4)

These queries were run against the local SQLite file `tasks.db`
(recommended viewer: DB Browser for SQLite).

## List every task

```sql
SELECT * FROM tasks;
```

| id | title | done |
|---:|---|---|
| 1 | Buy groceries | 0 |
| 2 | Write documentation | 1 |
| 3 | Review pull request | 0 |

## Show only completed tasks

```sql
SELECT * FROM tasks WHERE done = 1;
```

## Count all tasks

```sql
SELECT COUNT(*) FROM tasks;
```

## Mark every task as completed

```sql
UPDATE tasks SET done = 1;
```

## Delete all completed tasks

```sql
DELETE FROM tasks WHERE done = 1;
```

After changing rows directly in the database, `GET /tasks` immediately
reflects those changes because the API reads from SQLite on every request.

## Optional extras used by the API

```sql
SELECT * FROM tasks WHERE done = 1 ORDER BY id;

SELECT * FROM tasks WHERE title LIKE '%doc%' COLLATE NOCASE ORDER BY id;

SELECT
  COUNT(*) AS total,
  SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) AS done,
  SUM(CASE WHEN done = 0 THEN 1 ELSE 0 END) AS pending
FROM tasks;
```
