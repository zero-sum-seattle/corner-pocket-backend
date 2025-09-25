## Feature: Tournaments — Rack ’em up

### Why
Because it’s time to stop organizing matches in a group chat like a bunch of barbox bandits. Let’s add real tournament support so players can run the table without scratching on logistics.

### Summary
Add a Tournament feature that lets a user create a tournament, invite players, and manage basic details like description, location, date/time, and venue. Minimal viable brackets now, fancy chalk later.

### Scope
- **Models**: `Tournament`, `TournamentInvitation`
- **DB migrations**: Create tables for tournaments and invitations; add FK to `users`; optional FK to `venues` (see Venues feature).
- **API endpoints**: CRUD for tournaments, plus invitations create/list/accept/decline.
- **Auth**: Only tournament owners can edit/delete; invitees can respond; public read where appropriate.

### Requirements
- **Create tournament**: owner can set description, location text, date, time, and select a venue if available.
- **Invite players**: owner can invite users by user id or email (if we support email flow later). For now, by user id.
- **View**: list user-owned tournaments; list user-invited tournaments; get by id.
- **Update**: owner can update core fields until tournament is started (we’ll pretend “started” is a boolean for now).
- **Delete**: owner can delete a tournament that hasn’t started; otherwise, block and tell them the 8-ball doesn’t move.
- **Invitations**: create, list by tournament, accept, decline. Prevent duplicate active invites.
- **Validation**: date/time must be in the future at creation; venue (if set) must exist.

### Data Model (proposed)
- **Tournament**
  - `id` (uuid, pk)
  - `owner_id` (uuid → users.id, indexed)
  - `title` (text, optional but recommended)
  - `description` (text)
  - `location` (text) — freeform, e.g., “Back table by the jukebox”
  - `starts_at` (timestamp with tz)
  - `venue_id` (uuid → venues.id, nullable until Venues ship)
  - `is_started` (boolean, default false)
  - `is_archived` (boolean, default false)
  - `created_at` / `updated_at`
- **TournamentInvitation**
  - `id` (uuid, pk)
  - `tournament_id` (uuid → tournaments.id, indexed)
  - `invitee_user_id` (uuid → users.id, indexed)
  - `status` (enum: pending|accepted|declined|cancelled; default pending)
  - `created_at` / `updated_at`
  - Unique(`tournament_id`, `invitee_user_id`) on non-cancelled invites

### API Endpoints (v1)
- `POST /api/v1/tournaments` — create
- `GET /api/v1/tournaments/:id` — get
- `GET /api/v1/tournaments` — list (filters: `ownerId`, `invited=true`, `upcoming=true`)
- `PATCH /api/v1/tournaments/:id` — update (owner only, not started)
- `DELETE /api/v1/tournaments/:id` — delete (owner only, not started)
- `POST /api/v1/tournaments/:id/invitations` — invite users
- `GET /api/v1/tournaments/:id/invitations` — list invites
- `POST /api/v1/tournaments/:id/invitations/:inviteId/accept` — accept
- `POST /api/v1/tournaments/:id/invitations/:inviteId/decline` — decline

### Request/Response Sketches
- Create Tournament request
  - `{ title?, description, location, startsAt, venueId? }`
- Tournament response
  - `{ id, ownerId, title?, description, location, startsAt, venueId?, isStarted, createdAt }`
- Invitation create request
  - `{ inviteeUserIds: uuid[] }`

### DB Migrations
- Create `tournaments` table (fields above), index on `owner_id`, `starts_at`.
- Create `tournament_invitations` table with unique constraint per tournament+user for active invites.
- Add enum type for invitation `status` if DB requires.

### Security / Permissions
- Owners can CRUD their tournaments (with start-state restrictions).
- Invitees can read tournament summary and manage their own invite state.
- Public read allowed for tournament by id unless `is_archived`.

### Acceptance Criteria
- User can create a tournament with required fields; invalid past dates rejected.
- User can invite at least one player; duplicate invites are blocked.
- Invitee can accept/decline; status reflected in list.
- Owner can edit before start; cannot after start. Delete blocked if started.
- Endpoints return 401/403 appropriately when the cue ball says “nope”.

### Nice-to-haves (not in first rack)
- Email invites; shareable links; bracket generation.
- Soft-delete with restore; search/sort filters.

### Risks / Notes
- Time zones: keep everything in UTC, display is client problem (sorry, not sorry).
- Venue FK is nullable until Venues feature lands. We’ll circle back to pocket that ball.

### Definition of Done
- Models, migrations, and endpoints implemented with tests.
- Basic rate limits and input validation.
- API docs updated. No slop.
