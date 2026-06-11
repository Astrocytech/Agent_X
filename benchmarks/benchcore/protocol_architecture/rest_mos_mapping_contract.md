# REST/MOS Mapping Contract

## Purpose
Define the mapping between REST API endpoints and MOS (Media Object Server) protocol equivalents for the BenchCore benchmark pack. This contract establishes a mock-only translation layer for benchmark evaluation.

## Source
BENCHCORE-DOC-030

## Scope
**MOCK-ONLY.** This contract defines mappings for benchmark evaluation only. No real MOS connections, no real REST servers, and no production system interactions are implied or permitted.

## REST Endpoints and MOS Equivalents

| REST Endpoint | HTTP Method | MOS Equivalent | Description |
|---------------|-------------|----------------|-------------|
| `/api/stories` | GET | `MOS reqStoryList` | Retrieve list of stories |
| `/api/stories/:id` | GET | `MOS reqStory` | Retrieve a specific story |
| `/api/stories/:id` | POST | `MOS roStorySend` | Create or update a story |
| `/api/stories/:id` | PUT | `MOS roStorySend` | Replace a story |
| `/api/stories/:id` | DELETE | `MOS roStoryDelete` | Delete a story |
| `/api/fields` | GET | `MOS reqFieldList` | Retrieve field definitions |
| `/api/fields/:id` | POST | `MOS roFieldSend` | Create or update a field |
| `/api/commands` | POST | `MOS roCmd` | Send an arbitrary MOS command |

## Mapping Rules
1. **Method mapping**: REST GET maps to MOS `req*`, REST POST/PUT maps to MOS `ro*`, REST DELETE maps to MOS `ro*Delete`.
2. **Payload transformation**: REST JSON bodies are transformed to MOS XML payloads per the MOS protocol specification.
3. **Header mapping**: REST `Authorization` header maps to MOS `mosID` + `mosSchema` authentication fields.
4. **Error mapping**: REST HTTP status codes map to MOS error/ack responses:
   - 200 OK → `roAck`
   - 201 Created → `roAck` with ID
   - 400 Bad Request → `roNack` with error description
   - 404 Not Found → `roNack` with "not found" error
   - 500 Server Error → `roNack` with "internal error"

## Mock Implementation Notes
- All mappings are implemented as **pure functions** with no I/O dependencies.
- MOS payloads are constructed as XML strings or DOM objects, never sent over a network.
- REST requests are mocked as JSON objects matching `mock_rest_input.schema.json`.
- MOS responses are mocked as JSON objects matching `mock_mos_output.schema.json`.

## Constraints
- No live TCP, HTTP, or SSH connections.
- No real credentials, certificates, or API keys.
- No production MOS IDs or customer paths.
