# UI Planning Contract

## Status: DEFERRED

This document describes the planned UI components for the BenchCore human review interface. **No UI implementation exists yet.** This contract serves as a planning reference for future development.

## Source
BENCHCORE-DOC-023

## Plugin Concept
The BenchCore UI is planned as a plugin that integrates with the existing Inception frontend (within Agent_X). The plugin would provide:

1. **Suggestion Review Panel**: A dashboard displaying suggestion cards (`suggestion_card.schema.json`) for human review.
   - Cards grouped by suggestion type and sorted by confidence.
   - Inline accept/reject/modify actions.
   - Bulk action support (accept all, reject all).

2. **Feedback Log**: A chronological log of all feedback actions (`feedback_action.schema.json`).
   - Filterable by reviewer, action type, date range.
   - Exportable as JSON or CSV for audit.

3. **Explanation Viewer**: A modal or side panel displaying formatted customer-facing explanations (`customer_explanation_contract.md`).
   - Rendered from structured data, not pre-written text.
   - Copy-to-clipboard functionality.

## Inception Integration Plan
| Component | Integration Point | Status |
|-----------|------------------|--------|
| Suggestion Review Panel | New route under `/inception/benchcore/review` | Deferred |
| Feedback Log | New route under `/inception/benchcore/feedback` | Deferred |
| Explanation Viewer | Reusable component for both review and feedback pages | Deferred |
| UI State Store | New Pinia store module: `useBenchCoreReviewStore` | Deferred |
| Backend API | Mock API endpoints under `/api/benchcore/review/` | Deferred |

## Deferred Status Rationale
- Core grammar validation and data quality benchmarks must be stable before UI can be meaningfully tested.
- The suggestion card and feedback action schemas must be finalized through benchmark evaluation.
- No UI framework decision has been made beyond the existing Inception stack (Vue 3 + Pinia).
- No mock API has been implemented for the review workflow.

## Future Considerations
- Accessibility (a11y) compliance for reviewer-facing UI.
- Keyboard navigation for high-throughput review workflows.
- Internationalization (i18n) for customer-facing explanations.
- Dark mode support consistent with Inception theme.
