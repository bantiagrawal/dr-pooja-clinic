# App Delivery Plan (Persistent Agent Taskboard)

Last updated: 2026-03-20
Owner: Any active CLI agent (Codex or equivalent)

## Goal
Ship a production-ready mobile app where patients can authenticate, browse slots, book, view, and cancel appointments reliably.

## Definition of Done (Release v1)
- Patient can sign in (Google/Facebook) and complete auth fully in-app.
- Patient can view available slots filtered by duration.
- Patient can book a slot and see it in appointments immediately.
- Patient can cancel confirmed appointments and the slot is released.
- Profile screen supports read/update of key user fields.
- Android debug build is reproducible from repo.
- Core flows have automated smoke tests and a manual test checklist pass.

## Agent Working Protocol (Use Every Session)
1. Read `README.md`, `PROJECT_HANDOFF.md`, and this file.
2. Pick the first unchecked task `[ ]` in **Current Sprint**.
3. Mark it in-progress by changing `[ ]` to `[~]` with your initials/date.
4. Implement code + validation for that task only.
5. Mark complete `[x]` with short result note.
6. If blocked, add a blocker line under the task and move to next unblocked item.

## Current Sprint (Must-Have to Complete Booking App)

### A) Authentication Completion
- [ ] Implement mobile deep-link callback handling for Google OAuth code exchange.
- [ ] Implement mobile deep-link callback handling for Facebook token exchange.
- [ ] Persist tokens only after successful callback exchange; handle auth errors cleanly.
- [ ] Add logout + expired-token UX handling across all screens.

### B) Booking Flow Reliability
- [ ] Add loading/disabled states to prevent duplicate booking submissions.
- [ ] Add optimistic refresh path after booking so appointments list always reflects backend state.
- [ ] Add cancel confirmation + refresh path robustness for slow network/error cases.
- [ ] Handle empty slot states and API errors with consistent user messaging.

### C) Backend Hardening for Booking
- [ ] Add server-side validation for slot date/time (no booking past slots).
- [ ] Ensure race-safe booking behavior (single winner on same slot under concurrent requests).
- [ ] Trigger cancellation notification task on cancel endpoint.
- [ ] Restrict/remove `/api/dev/token` behind environment guard.

### D) Security + Configuration
- [ ] Replace plain-file token storage with secure platform storage strategy.
- [ ] Tighten CORS configuration for non-dev environments.
- [ ] Move secrets/config review into documented env policy (`.env.example` alignment).

### E) Packaging + Testability
- [ ] Add `buildozer.spec` and document Android build prerequisites.
- [ ] Add API smoke tests for booking endpoints (`slots`, `book`, `list`, `cancel`).
- [ ] Add mobile manual QA checklist and pass criteria for booking release.

## Next Sprint (Should-Have)
- [ ] Add appointment reschedule flow.
- [ ] Add slot date picker and richer filters.
- [ ] Add push/local reminders integration in mobile.
- [ ] Add basic admin web UI for slot template management.

## Validation Checklist for Release v1
- [ ] OAuth login works end-to-end on device/emulator.
- [ ] Booking a slot updates appointments screen in same session.
- [ ] Cancelling frees slot and reflects in availability list.
- [ ] No duplicate bookings under repeated tap/network retry.
- [ ] Android debug APK builds successfully from clean environment.

## Session Log (Append Newest First)
- 2026-03-20: Initial persistent plan created from current codebase status.
