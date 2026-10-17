# CIAO production deployment runbook

This runbook describes the production preparation and update process. The
repository does not contain a production host, domain, TLS certificate, or
mail/broker provider configuration, so completing these steps does not deploy
the service by itself.

## Before the first release

1. Provision PostgreSQL with automated encrypted backups, a tested restore
   process, and a network policy that only permits the API and operators.
2. Provision an MQTT broker with TLS for device connections. The current
   `emqx/base.hocon` configures HTTP authentication/ACLs but does not configure
   a TLS listener. Do not expose the development broker's port 1883 or
   dashboard port 18083 to the public internet.
3. Put the API behind a TLS reverse proxy or managed ingress. Forward only
   HTTPS traffic to the API and configure a fixed web origin where applicable.
4. Create secrets outside the repository. At minimum configure `DB_USER`,
   `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `JWT_SECRET_KEY`,
   `SECRET_KEY`, `EMQX_AUTH_SECRET`, `MQTT_USERNAME`, `MQTT_PASSWORD`,
   `DEBUG=False`, and `CORS_ALLOWED_ORIGINS` as a JSON array of exact origins.
   Keep JWT and application signing keys distinct and rotate them through a
   planned release because rotation invalidates existing sessions.
5. Configure SMTP (`MAIL_HOST`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`,
   `MAIL_FROM`, `MAIL_STARTTLS`) and set `PASSWORD_RESET_URL` to the app's
   verified deep link. Password recovery returns 503 until SMTP host and
   sender are configured.
6. Configure TLS and credentials for the broker-to-API network path, then
   verify EMQX authentication and ACL behavior with a test device before
   migrating production traffic.

## Release and update procedure

1. Build an immutable image from the reviewed commit and deploy it to a
   staging environment first.
2. Back up the production database and verify that the backup is readable.
3. Review the Alembic SQL/diff and migration downgrade path. Apply
   `alembic upgrade head` once as a release job before rolling out API
   instances; do not let every API replica run migrations on startup.
4. Roll out the API image, check `/health`, inspect structured logs and
   `X-Request-ID` correlation, then exercise login, password reset, device
   authentication, telemetry ingestion, and command delivery.
5. Keep the previous image available for rollback. If a migration is not
   backward-compatible, restore the backup or use a reviewed forward-fix;
   do not assume application rollback reverses a database migration.

## Operations

- Alert on API error rate/latency, database capacity, broker availability,
  command outbox age, and repeated MQTT authentication failures.
- Store logs and backups outside the application container, restrict access,
  and set retention appropriate to local privacy and regulatory requirements.
- Test database restore and application rollback on a schedule.
- The repository has no approved `datastream_values` retention period yet.
  Do not add an automatic purge until that period and any required archival
  behavior are agreed.
- `docker-compose.yml` is a development stack: it exposes development
  services and contains development defaults. Do not use it as a production
  deployment manifest.
