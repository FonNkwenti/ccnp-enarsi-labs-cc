# Track: refresh_lab.py — Load Initial Configs Instead of Solutions

**Status**: Complete
**Date**: 2026-02-12

## Summary

All 9 EIGRP `refresh_lab.py` scripts were loading solution configs instead of initial configs.
Changed every device path from `solutions/Rx.cfg` to `initial-configs/Rx.cfg` and updated the
closing message accordingly.

## Files Changed

- `labs/eigrp/lab-{01..09}/scripts/refresh_lab.py` (9 files) — Point to `initial-configs/`.
