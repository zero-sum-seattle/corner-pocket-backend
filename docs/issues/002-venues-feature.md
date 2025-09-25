## Feature: Venues — Where the felt meets the flex

### Why
Tournaments without venues are like break shots without chalk: messy and unnecessary. Venues let pool halls list themselves, advertise, and be tied to tournaments so players know where to show up and pretend they always call their pockets.

### Summary
Add a Venues resource with CRUD endpoints so pool halls (and other spots with tables) can create profiles. Future: verification and promos. For now, keep it tight and straight as a center-ball hit.

### Scope
- **Models**: `Venue`
- **DB migrations**: Create venues table; later tie to tournaments via `venue_id`.
- **API endpoints**: CRUD + list with search filters (name, city/state, amenities later).

### Requirements
- **Create venue**: name, address fields, optional website/contact, description, table count, and basic metadata.
- **Read**: get by id; list with filters and pagination.
- **Update/Delete**: owner/admin-only; soft delete optional later.
- **Tournament link**: tournaments can reference `venue_id` (nullable until this ships). Enforce FK after both features are live.

### Data Model (proposed)
- **Venue**
  - `id` (uuid, pk)
  - `name` (text, required)
  - `description` (text)
  - `address_line1` (text)
  - `address_line2` (text, nullable)
  - `city` (text)
  - `state` (text)
  - `postal_code` (text)
  - `country` (text, default "US")
  - `latitude` / `longitude` (numeric, nullable)
  - `phone` (text, nullable)
  - `website_url` (text, nullable)
  - `table_count` (integer, default 0)
  - `amenities` (jsonb, nullable) — things like "bar", "snacks", "tournaments"
  - `is_active` (boolean, default true)
  - `created_at` / `updated_at`

### API Endpoints (v1)
- `POST /api/v1/venues` — create
- `GET /api/v1/venues/:id` — get
- `GET /api/v1/venues` — list (filters: `q`, `city`, `state`, `isActive`)
- `PATCH /api/v1/venues/:id` — update
- `DELETE /api/v1/venues/:id` — delete (soft delete optional later)

### Request/Response Sketches
- Create Venue request
  - `{ name, description?, addressLine1?, addressLine2?, city?, state?, postalCode?, country?, phone?, websiteUrl?, tableCount?, amenities? }`
- Venue response
  - `{ id, name, description?, address..., city?, state?, postalCode?, country?, phone?, websiteUrl?, tableCount, amenities?, isActive, createdAt }`

### DB Migrations
- Create `venues` table with indexes on `name`, `city`, `state`, and optional `is_active`.
- Later migration: add FK `tournaments.venue_id → venues.id` (if not already nullable present) and set to not-null only when UX supports it.

### Security / Permissions
- Venue create/update/delete limited to authenticated venue owners or admins (we’ll keep the sharks honest).
- Public read for active venues.

### Acceptance Criteria
- Venue can be created with at least name; optional fields stored when provided.
- List endpoint supports pagination and basic search by `q` (name/description), city, state.
- Update/delete are permission-checked; 401/403 returned when someone tries to hustle the API.
- Tournaments can reference `venue_id` when creating/editing; FK validates when present.

### Nice-to-haves (not in first rack)
- Geosearch by radius; hours of operation; verified badge; photos.

### Risks / Notes
- Addresses are a swamp; we’ll keep it freeform now and normalize later.
- Amenity taxonomy can explode like a mis-cued break; keep it json until stable.

### Definition of Done
- Model, migrations, and endpoints implemented with tests.
- Basic validation and pagination.
- API docs updated. No slop.
