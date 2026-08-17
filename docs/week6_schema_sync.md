# Week 6 - user_features schema sync

The Week 6 behaviour pipeline and `UserFeatures` ORM model use the following
application-owned feature columns:

- total_xp
- preferred_language
- onboarding_goal
- age_proxy
- city_tier
- time_of_day
- session_duration
- screens_visited
- lessons_started
- quizzes_taken

If an existing PostgreSQL `user_features` table was created before the Week 6
columns were added, `Base.metadata.create_all()` will not alter that existing
table. Run the idempotent sync script once:

```bash
cd /mnt/c/Projects/financial-ai-platform
source .venv/bin/activate
python -m scripts.sync_user_features_schema
```

Then test the feature pipeline:

```bash
python -m app.pipelines.feature_pipeline
```

The script only adds missing columns and does not delete or recreate existing
data.
