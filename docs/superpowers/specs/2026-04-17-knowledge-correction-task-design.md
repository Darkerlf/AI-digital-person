# Knowledge Correction Task Design

## 1. Goal

Upgrade the current missed-question repair flow from a manual jump-and-edit process to a traceable knowledge-correction loop that records how an unresolved session issue becomes a FAQ or knowledge document update.

This slice must let admins:

- create a correction task from an unresolved question
- choose whether the correction path is `faq` or `document`
- continue the task from the FAQ page or knowledge-document page
- link the created FAQ or document back to the task
- mark the task resolved after a real knowledge artifact exists

This slice must also let the backend:

- prevent duplicate active tasks for the same unresolved message
- keep a durable relationship between the source message and the final knowledge artifact
- sync task completion back to the original missed-question resolution state

## 2. Scope

### In Scope

- `knowledge_correction_task` data model
- task CRUD-lite APIs for list, create, detail, link, and resolve
- session-management page enhancement for task creation and task continuation
- FAQ page query-prefill and task-link flow
- knowledge-document page query-prefill and task-link flow
- a task list view for correction progress tracking
- backend and frontend automated tests for the new loop

### Out Of Scope

- assignee workflow
- comments or discussion threads
- priority or SLA fields
- batch task operations
- automatic correction-type recommendation
- linking one task to multiple FAQ or document results

## 3. Selected Approach

Use a dedicated correction-task model as the center of the loop.

The unresolved conversation message remains the source signal, but it is no longer the only record of the repair process. Once an admin chooses to act, the system creates a correction task that persists correction type, current status, linked result, and operator notes. FAQ and knowledge-document creation flows then link their newly created records back to the task and can complete the loop.

This keeps process tracking explicit without turning the project into a general-purpose ticketing system.

## 4. Data Model

### 4.1 `knowledge_correction_task`

- `id`
- `source_message_id`
- `session_id`
- `scenic_area_id`
- `question_text`
- `recognized_text`
- `feedback_status`
- `correction_type`
  - `faq`
  - `document`
- `status`
  - `open`
  - `resolved`
- `resolution_note`
- `linked_faq_id`
- `linked_document_id`
- `created_by`
- `resolved_by`
- `created_at`
- `updated_at`

### 4.2 Constraints

- one unresolved message can have at most one active `open` correction task
- one task can link only one result type
- `faq` tasks can only use `linked_faq_id`
- `document` tasks can only use `linked_document_id`
- a task can be resolved only after the correct linked result exists

## 5. State Flow

### 5.1 Task Creation

- source data comes from `conversation_message`
- admin chooses `faq` or `document`
- system creates an `open` task

### 5.2 Task Continuation

- the task can be reopened from the session page or the dedicated task list page
- the frontend sends task context through route query parameters into FAQ or document creation forms

### 5.3 Task Resolution

- after a FAQ is created and linked, a `faq` task can be resolved
- after a knowledge document is created and linked, a `document` task can be resolved
- resolving the task updates the original message repair state to `resolved`

## 6. Backend API Design

### 6.1 Task Endpoints

- `GET /api/knowledge/correction-tasks`
- `POST /api/knowledge/correction-tasks`
- `GET /api/knowledge/correction-tasks/{id}`
- `PUT /api/knowledge/correction-tasks/{id}/link-faq`
- `PUT /api/knowledge/correction-tasks/{id}/link-document`
- `PUT /api/knowledge/correction-tasks/{id}/resolve`

### 6.2 Create Request

- `source_message_id`
- `correction_type`
- `resolution_note`

### 6.3 List Filters

- `status`
- `correction_type`
- `scenic_area_id`

### 6.4 Detail Response

- task fields
- source session key
- current linked FAQ or linked document summary when present

## 7. Frontend Design

## 7.1 Session Management View

Enhance each unresolved item with:

- `创建 FAQ 修正任务`
- `创建文档修正任务`
- current task status when a task already exists
- `继续处理` action when a task already exists

The page should stop using a generic “mark resolved” action as the main path. Resolution should come from the linked task flow.

## 7.2 FAQ View

Add support for query-prefill inputs:

- `taskId`
- `question`
- `scenicAreaId`

Behavior:

- prefill the FAQ question and scenic area
- after successful FAQ creation, call `link-faq`
- if link succeeds, allow immediate task completion

## 7.3 Knowledge Document View

Add support for query-prefill inputs:

- `taskId`
- `question`
- `recognizedText`
- `scenicAreaId`

Behavior:

- prefill scenic area
- prefill title or content draft using the missed question context
- after successful document creation, call `link-document`
- if link succeeds, allow immediate task completion

## 7.4 Correction Task View

Add `KnowledgeCorrectionTaskView` with:

- task list
- status filter
- correction-type filter
- source question preview
- linked-result preview
- continuation entry back into FAQ or document creation

This page is important for demo value because it shows the repair loop as an explicit operational process.

## 8. Error Handling

### 8.1 Backend

- duplicate active task for the same message -> `409`
- resolve without linked FAQ or document -> `400`
- task not found -> `404`
- linked FAQ or document not found -> `404`

### 8.2 Frontend

- if a task already exists, the session page should not create another one
- if linking fails, the task stays `open`
- task completion is never assumed from form submission alone; the link result is required first

## 9. Testing Strategy

### 9.1 Backend

Add tests for:

- create a FAQ correction task from an unresolved message
- reject duplicate active task creation for the same message
- link FAQ and resolve task
- link knowledge document and resolve task
- task resolution updates the original message repair state

### 9.2 Frontend

Add tests for:

- session page renders task-creation actions
- FAQ page reads query-prefill data
- knowledge-document page reads query-prefill data
- successful FAQ or document creation triggers task-link API call
- task list page renders `open` and `resolved` states with linked-result information

## 10. Risks And Constraints

- this slice intentionally tracks one result per task; parallel FAQ and document repair for one issue is explicitly excluded from this implementation slice
- task resolution depends on existing FAQ and document creation flows staying simple and deterministic
- the operational value comes from traceability, not workflow complexity; adding generic ticket-system features would dilute the slice
