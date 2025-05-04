# TODO - stock_data_poller

This document tracks the outstanding tasks and potential enhancements needed to bring the `stock_data_poller` project to MVP and beyond.

---

## 🔧 Core Features

- [ ] Add `BasePoller.poll()` return payload documentation and standard schema.
- [ ] Standardize poller-specific payload formats to match a shared data contract.
- [ ] Validate API responses against schemas (e.g. `pydantic` or `jsonschema`).
- [ ] Handle empty, malformed, or rate-limited API responses gracefully.
- [ ] Add historical data support for backfilling.

---

## ⚙️ Configuration & Secrets

- [ ] Implement environment validation on startup for all pollers.
- [ ] Add fallback defaults for missing but non-critical configurations.
- [ ] Integrate with AWS Secrets Manager as a fallback to Vault.
- [ ] Validate Vault integration and secrets fetching during CI lint/test.

---

## 📬 Queue & Messaging Enhancements

- [ ] Support message batching to reduce network overhead.
- [ ] Add retry + DLQ support for RabbitMQ (requeue on NACK).
- [ ] Add visibility timeout + retry tracking for SQS.

---

## 🧠 Slack Integration

- [ ] Integrate optional Slack notifications on:
  - Poller failures
  - Retry exhaustion
  - Startup and shutdown events
- [ ] Add `SLACK_WEBHOOK_URL` config support.
- [ ] Support disabling Slack via `ENABLE_SLACK_ALERTS`.

---

## 💾 Caching Strategies

- [ ] Add per-symbol result caching to reduce duplicate API calls.
- [ ] Support local memory cache and optional Redis.
- [ ] TTL configuration via `CACHE_TTL_SECONDS` env var.
- [ ] Cache failed symbols separately to avoid redundant failures.

---

## 🚀 Performance & Optimization

- [ ] Optimize rate limiter logic to avoid excessive token overhead.
- [ ] Move `send_to_queue()` to a worker thread pool for async dispatch.
- [ ] Profile API call latency and queue latency metrics.
- [ ] Add optional multiprocessing for symbol polling in parallel.
- [ ] Introduce async support for non-blocking IO operations.

---

## 🧪 Testing & Validation

- [ ] Add unit tests for all pollers with mock APIs.
- [ ] Add integration tests that simulate full polling loop.
- [ ] Add validation tests for queue delivery.
- [ ] Ensure 90%+ code coverage via `pytest-cov`.
- [ ] Add test coverage badge to `README.md`.

---

## 🧼 Code Quality & Tooling

- [ ] Enforce type-checking with `pyright` or `mypy` in CI.
- [ ] Add `bandit` and `safety` security scanning to pre-commit.
- [ ] Auto-format with `black` and `ruff`.
- [ ] Add markdown linting and code spell-checking.
- [ ] Enforce docstring presence in all public modules.

---

## 🔍 Observability

- [ ] Add Prometheus-compatible metrics endpoint.
- [ ] Expose rate limiter state and queue size.
- [ ] Add structured JSON logging for ingestion by ELK or CloudWatch.
- [ ] Integrate optional OpenTelemetry traces.

---

## 📦 Packaging & Deployment

- [ ] Add Docker support with entrypoint configuration.
- [ ] Push Docker images to GitHub Container Registry.
- [ ] Add Helm chart or Kustomize overlays for k8s deployment.
- [ ] Support environment-specific config via config maps or SSM.

---

## 🧭 Future Enhancements

- [ ] Add support for additional providers: Intrinio, TwelveData, Barchart.
- [ ] Support fetching sector or ETF-level data.
- [ ] Add scheduled CRON job polling mode.
- [ ] Add CLI support for one-time fetches or dry-runs.
- [ ] Implement alerting logic for anomalies (e.g. price spikes).
