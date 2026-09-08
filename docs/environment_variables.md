# AI-service environment variables

| Variable | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | For LLM calls | Gemini API credential; never log it |
| `GEMINI_MODEL` | No | Gemini model name |
| `SHARED_SECRET` | Development/production | Shared secret expected in `X-API-KEY` |
| `AI_AUTH_ALLOW_LOCAL` | No | Explicit local-only auth bypass; keep `false` outside tests |
| `SENTRY_DSN` | No | Sentry error tracking DSN |
| `SENTRY_ENVIRONMENT` | No | Sentry environment label |
| `REDIS_HOST` | For Redis features | Redis hostname |
| `REDIS_PORT` | For Redis features | Redis port |
| `REDIS_PASSWORD` | No | Redis password |
| `REDIS_SSL` | No | Enable TLS for Redis (`false` locally) |
| `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD` | DB-backed features | PostgreSQL connection |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka collector | Kafka brokers |
| `KAFKA_ORDERS_TOPIC` | Kafka collector | Orders topic |
| `KAFKA_COMPLIANCE_TOPIC` | Fraud alert integration | Compliance alert topic |
| `KAFKA_CONSUMER_GROUP` | Kafka collector | Consumer group |

Never put `GEMINI_API_KEY`, `SHARED_SECRET`, database passwords, or raw personal data in logs.
