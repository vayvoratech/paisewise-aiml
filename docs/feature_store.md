# Feature Store Documentation

## 1. Purpose

The feature store provides the latest user-level features required by the AI/ML services.

The AI service reads feature data from the production `user_features` table. Feature calculation and updates are handled outside the AI service by backend/data pipelines.

The AI service does **not** calculate or modify feature values.

---

## 2. Production Feature Store Table

### Table: `public.user_features`

The production feature store is represented by the `user_features` table.

The table stores aggregated behavioral and engagement features for each user.

### Primary Key

```text
user_id
```

`user_id` uniquely identifies the user and references the production `users` table.

---

## 3. Features

The current production `user_features` table contains the following features.

### Quiz Activity

- `quiz_attempts_total`
- `quiz_pass_rate`
- `avg_quiz_score`

These represent the user's quiz activity and performance.

### User Identification

- `user_id`

Uniquely identifies the user and references the production `users` table.

### Feature Freshness

- `computed_at`

Indicates when the feature values were computed.

## 4. Data Ownership

| Component               | Responsibility                            |
| ----------------------- | ----------------------------------------- |
| Backend / Data Pipeline | Calculate and update user features        |
| Production Database     | Store the latest feature values           |
| AI Service              | Read feature values                       |
| Recommendation Service  | Use relevant features for recommendations |
| Monitoring              | Detect feature/data distribution changes  |

The AI service should remain read-only with respect to the feature store.

---

## 5. AI Service Feature Access

The AI service retrieves the latest features using:

```text
GET /features/{userId}
```

The corresponding service implementation is:

```text
services/feature_service.py
```

The service queries the production table:

```sql
SELECT
    user_id,
    quiz_attempts_total,
    quiz_pass_rate,
    avg_quiz_score,
    computed_at
FROM public.user_features
WHERE user_id = %s
LIMIT 1;
```

The query retrieves the feature values required by the current AI service implementation.

---

## 6. Feature Retrieval Flow

```text
Production Application
        |
        v
Feature Calculation / Data Pipeline
        |
        v
public.user_features
        |
        |  Read
        v
AI Service
        |
        v
Feature Service
        |
        v
GET /features/{userId}
```

The AI service consumes the latest available feature vector rather than independently recalculating features.

---

## 7. Temporary-to-Production Migration

The previous implementation used a temporary feature table:

```text
feature_vectors
```

The production schema provides:

```text
user_features
```

Therefore, the AI service has been migrated from the temporary feature source to the production feature store.

### Mapping

| Temporary Source                      | Production Source                   |
| ------------------------------------- | ----------------------------------- |
| `feature_vectors.user_id`             | `user_features.user_id`             |
| `feature_vectors.quiz_attempts_total` | `user_features.quiz_attempts_total` |
| `feature_vectors.quiz_pass_rate`      | `user_features.quiz_pass_rate`      |
| `feature_vectors.avg_quiz_score`      | `user_features.avg_quiz_score`      |
| `feature_vectors.computed_at`         | `user_features.computed_at`         |

Additional production features are available in `user_features` and can be consumed by AI/ML services when required.

---

## 8. Data Freshness

Feature values are generated outside the AI service and stored in the production database.

The `computed_at` field indicates when the feature values were computed.

The AI service should use the latest available feature record.

Data freshness should therefore be monitored as part of the data-quality monitoring framework.

---

## 9. Data Quality Requirements

The following checks should be performed on the feature store:

### Completeness

Verify that required features are not unexpectedly null.

### Validity

Feature values should follow the expected data types and valid ranges.

Examples:

```text
quiz_pass_rate → 0 to 1
avg_quiz_score → 0 to 1
quiz_attempts_total → non-negative
lessons_completed_total → non-negative
streak_days_current → non-negative
```

### Freshness

Check whether feature records are being updated within the expected time window.

### Distribution Stability

Monitor feature distributions over time and detect significant shifts.

A distribution shift greater than the configured threshold should generate an alert for investigation.

---

## 10. Monitoring

The feature monitoring component is responsible for monitoring feature distributions.

Current implementation:

```text
services/feature_monitor.py
```

The monitoring process calculates feature distributions and compares them with historical distributions.

A distribution shift greater than **20%** is treated as an alert condition in the current implementation.

Monitoring results can be stored in:

```text
feature_distribution_history
```

---

## 11. Security and Access

The feature store contains user-level application data.

Therefore:

* The AI service should use controlled database access.
* The AI service should perform read-only operations on the feature store.
* User identification should be validated before retrieving features.
* Database credentials must be provided through environment configuration.
* Database credentials must not be hardcoded in source code.

---

## 12. Current Status

| Item                                  | Status      |
| ------------------------------------- | ----------- |
| Production feature table identified   | Complete    |
| Temporary `feature_vectors` mapping   | Complete    |
| AI feature retrieval service          | Complete    |
| `GET /features/{userId}`              | Complete    |
| Feature distribution monitoring       | Complete    |
| Data-quality monitoring documentation | In progress |
| Automated daily data-quality report   | Next step   |

---

## 13. Next Step

The next implementation task is to create a **daily feature-store data-quality report** covering:

1. Feature completeness
2. Null values
3. Invalid/out-of-range values
4. Feature freshness
5. Distribution changes
6. Overall data-quality status

The report should provide a simple summary that can be reviewed by the AIML team and used to identify data issues before they affect downstream AI/ML services.
