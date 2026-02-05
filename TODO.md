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
- [ ] User to test after changes
