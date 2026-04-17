# Route Template And Recommendation Design

## 1. Goal

Add route-template management and a route-recommendation API that can support the future visitor-side recommendation flow without requiring a second backend redesign.

This slice must let admins:

- create and maintain route templates
- configure interest tags, audience tags, duration bounds, and ordered scenic spots
- preview recommendation results in the admin UI

This slice must let the backend:

- select the best matching route template for a recommendation request
- return a stable, explainable recommendation result
- fall back to the nearest template when no exact template matches

## 2. Scope

### In Scope

- backend route-template data model
- backend CRUD APIs for route templates
- backend recommendation generation API
- admin route-template management page
- admin recommendation preview panel
- automated backend tests for CRUD and recommendation matching
- frontend render-level verification plus full build/test verification

### Out Of Scope

- visitor-side mini-program route page
- map navigation and GPS routing
- LLM-generated recommendation copy
- multi-template stitching
- dynamic ranking from live behavior events
- route feedback write-back

## 3. Selected Approach

The implementation uses a mixed template model:

- a template can carry fixed ordered scenic spots
- a template can also carry rule-oriented metadata for future extension
- the current recommendation engine always prefers fixed ordered spots when present

The recommendation API is designed for future visitor-side use now, not as a temporary admin-only payload. Inputs use interest tags, duration, audience tags, and an optional scenic area. Outputs include the matched template, fallback state, match reason, summary, and ordered spots with stay-time suggestions.

When no exact template matches, the service returns the nearest active template instead of failing empty.

## 4. Data Model

### 4.1 `route_template`

- `id`
- `scenic_area_id`
- `name`
- `template_type`
  - `fixed`
  - `hybrid`
- `interest_tags_json`
- `audience_tags_json`
- `duration_min_minutes`
- `duration_max_minutes`
- `summary`
- `status`
  - `active`
  - `inactive`
- `priority`
- `rule_notes`
- `created_at`
- `updated_at`

### 4.2 `route_template_spot`

- `id`
- `template_id`
- `scenic_spot_id`
- `sort_order`
- `stay_minutes`
- `highlight`
- `created_at`
- `updated_at`

## 5. Backend API Design

### 5.1 Route Template CRUD

- `GET /api/route-templates`
- `POST /api/route-templates`
- `GET /api/route-templates/{id}`
- `PUT /api/route-templates/{id}`
- `DELETE /api/route-templates/{id}`

Route-template reads should include nested `spots` so the admin page can edit a full template without a second API call.

### 5.2 Recommendation Generation

- `POST /api/route-recommendations/generate`

Request:

- `scenic_area_id`
- `interest_tags`
- `duration_minutes`
- `audience_tags`

Response:

- `matched_template`
- `fallback_used`
- `match_reason`
- `summary`
- `spots`
  - `scenic_spot_id`
  - `name`
  - `stay_minutes`
  - `highlight`

## 6. Recommendation Logic

### 6.1 Filtering

Only `active` templates participate. Templates are first filtered by `scenic_area_id` when provided.

### 6.2 Scoring

Each candidate template is ranked by:

1. duration exactness
2. interest-tag overlap count
3. audience-tag overlap count
4. template priority

### 6.3 Exact Match

An exact match means:

- duration is within `[duration_min_minutes, duration_max_minutes]`
- at least one interest tag overlaps when interest tags are provided

Audience-tag overlap improves ranking but does not block eligibility.

### 6.4 Fallback

If no exact template exists, return the highest-ranked candidate and set:

- `fallback_used = true`
- a human-readable `match_reason`

Typical fallback reasons:

- duration range relaxed
- audience match weaker than preferred
- no full tag match but closest cultural theme found

### 6.5 Result Construction

When a template contains ordered route spots, return them in `sort_order` order. The summary comes from the template summary field for now. This keeps results deterministic and avoids introducing generated copy before the visitor-side route flow exists.

## 7. Admin UI Design

Add `RouteTemplateView` with three work areas:

### 7.1 Template Form

Fields:

- template name
- scenic area
- template type
- interest tags
- audience tags
- min duration
- max duration
- summary
- status
- priority
- rule notes

### 7.2 Ordered Spot Editor

For each route stop:

- scenic spot
- sort order
- stay minutes
- highlight

### 7.3 Template List And Preview

The page also includes:

- template list with edit/delete actions
- recommendation preview form using the future visitor-side request payload
- preview result section showing matched template, fallback status, reason, and ordered route spots

## 8. Testing Strategy

### 8.1 Backend

Add tests for:

- template CRUD
- recommendation generation with exact match
- recommendation generation with nearest-template fallback

### 8.2 Frontend

Add a render-level test for `RouteTemplateView` and rely on:

- `npm.cmd run test`
- `npm.cmd run build`

for slice verification.

## 9. Risks And Constraints

- Scenic-spot metadata is still shallow, so current recommendation quality depends mainly on template curation rather than dynamic intelligence.
- Fixed ordered spots are the primary delivery path in this slice; hybrid rule fields are reserved but not deeply exploited yet.
- If the visitor-side route flow later needs map routing or richer copy, those should be layered on top of this API rather than replacing it.
