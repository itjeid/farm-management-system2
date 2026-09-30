# Worldwide Maintenance & Improvement Plan

This project keeps the existing database schema and records. Future structural changes should be additive and migrated carefully.

## Safe release process
1. Back up the production database.
2. Test the new release against a copy of production data.
3. Run application tests and verify login, permissions, CRUD, finance, reports and AI.
4. Deploy to staging first.
5. Monitor errors and database performance.
6. Deploy to production.
7. Keep a rollback package and database backup.

## International expansion
- Add timezone-aware dates and timestamps.
- Add country-specific currency formatting.
- Expand translation catalogs beyond English/Kinyarwanda.
- Add regional units (litres, kilograms, acres/hectares, etc.).
- Add configurable tax/accounting rules by country.
- Add privacy, retention and consent controls.
- Use PostgreSQL in production and automated backups.
- Add audit logs for every admin change.
- Add role permissions beyond admin/user.
- Add monitoring, rate limiting and security alerts.
- Keep veterinary AI as decision support, not a replacement for a veterinarian.
- Version AI prompts/models and review model outputs periodically.

## Database rule
Do not delete or recreate the existing database during upgrades. New tables may be introduced only after a backup and explicit migration plan. Existing records must remain recoverable.
