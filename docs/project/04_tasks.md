# Task status

Status is based on repository code and local artifacts reviewed on 2026-10-26,
not on presumed completion of a branch or assignment. Existing task IDs are
retained for continuity. "Implemented" does not mean performance was validated.

| ID | Task | Current status and evidence |
|---|---|---|
| T-01 | Research coding datasets | Documented; TACO is the local source. The earlier GSM8K task wording did not match this coding project. |
| T-02 | Document sources and use conditions | Source records exist; dataset/platform terms are not enforced by the prompt-only exporter. |
| T-03 | Select initial data | TACO implemented; LiveCodeBench remains an optional local-file import. |
| T-04 | Define difficulty labels | Pending measured solution-test results. |
| T-05 | Prepare LLM generation | Implemented: `GenerationConfig`, `ResponseGenerator`, `BatchGenerator`, `OllamaGateway`. |
| T-06 | Define application API | Implemented request/response schemas for provisional prediction. |
| T-07 | Create backend | Implemented with FastAPI and static frontend serving. |
| T-08 | Temporary prediction endpoint | Implemented with keyword/length heuristics, not a trained model. |
| T-09 | Select frontend technology | Plain HTML, CSS and JavaScript are present. |
| T-10 | Frontend skeleton | Implemented. |
| T-11 | Prompt input interface | Implemented, including examples and result display. |
| T-12 | Frontend/backend integration | API calls and local fallback implemented. |
| T-13 | Generate labeled dataset | Pending; saved generated responses are not correctness labels. |
| T-14 | Prepare labeled training data | Pending T-13. |
| T-15 | Baseline model | Not implemented. |
| T-16 | Neural architecture | Not implemented. |
| T-17 | Neural network | Not implemented. |
| T-18 | Training pipeline | Not implemented. |
| T-19 | Train initial network | Not implemented. |
| T-20 | Evaluate network | Not implemented. |
| T-21 | Model experiments | No trained-predictor experiments implemented. |
| T-22 | Select final predictor | Pending. |
| T-23 | Export trained model | No trained model artifact present. |
| T-24 | Integrate trained predictor | Pending; current API remains provisional. |
| T-25 | Data audit | Structural auditor and stored reports implemented; solution-test validity is unverified. |
| T-26 | EDA | Difficulty grouping and stored summaries exist; full labeling-oriented analysis remains pending. |

## Gaps affecting the next experiment

- Preserve source IDs and dataset provenance alongside the SHA-256 prompt ID.
- Resolve repeated TACO texts without arbitrarily choosing one problem's tests.
- Connect the selected candidate list to the actual evaluated prompts.
- Provide an isolated test runner; none exists in the current code tree.

Only `tests/test_api_endpoints.py` is currently present as an automated test
module. Its API checks do not validate data provenance, generation recovery,
model quality or sandbox safety.
