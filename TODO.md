# TODO: Drum Dungeon DevOps Project - Phase 1 Cleanup

## Phase 1.1: Remove dead & legacy code
- [x] Move legacy scripts to app/scripts/_legacy/ (already done)
- [x] Remove unused imports in main.py (subprocess, sys)
- [x] Ensure no subprocess calls (none present)

## Phase 1.2: Centralize configuration
- [x] Create app/config.py with PRACTICE_DATA_DIR, ENV
- [x] Update imports in main.py and auth.py to use config.py

## Phase 1.3: Finalize stats schema
- [x] Review and ensure consistent initial stats creation in main.py

## Testing
- [x] User to test after changes

## Phase 2.1: MariaDB for Dual write, more Docker ready
- [x] Create JSON storage to MariaDB migration plan

## Phase 2.2:  Database design
- [x] Clean 1:1 mapping from JSON to DB tables users, students, xp, attendance, streaks, history_events

## Phase 2.3: Migration Strategy (Dual-Write)
- [x] The dual-write system is fully implemented
- [x] Keep JSON - All reads still from JSON files
- [x] Also write to DB - All writes sync to MariaDB
- [x] Safe & reversible - Can rollback to JSON-only anytime