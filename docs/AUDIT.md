# Repository audit

Reviewed on 29 October 2026. This review covers the tracked backend routes, models, services, setup and migration scripts, frontend pages/components/contexts, dependencies and documentation. Source inspection and executed checks are distinguished below.

## Assessment

The project has a useful application structure and a reasonable pretrained embedding baseline. Its strongest part is the complete workflow around matching: upload, discovery, skill comparison, bookmarking and application tracking. Before this pass, several features described in the documentation could not work together because the frontend, routes and models used different contracts.

It should be presented as a working application prototype. There is no labeled relevance benchmark, comparison against keyword retrieval, or evidence that the score measures employability. Calling its template-based skill explanations “explainable AI” overstates what they establish. The parser uses regular expressions and a fixed skill vocabulary; installing spaCy did not make it an NLP entity extraction pipeline.

## Repaired findings

| Area | Finding | Change |
| --- | --- | --- |
| Installation | JWT, password hashing and email-validation imports had no declared dependencies. | Added the required packages and direct bcrypt hashing with legacy hash verification; removed unused runtime libraries. |
| Resume access | Uploads used a shared demo email, attempted to create users without required hashes, and exposed resume/match routes without ownership checks. | Require authentication and scope reads, deletion, ranking and history to the current user. |
| Uploads | Original filenames were used in storage paths; second-resolution names could collide. Empty-page text extraction could fail. | UUID storage names, bounded streaming, PDF signature checks, readable-text validation and rollback/file cleanup. |
| Job search | Skill filtering referenced an undefined `String`. | Added the import and checked the filtered route. |
| Saved jobs | `/jobs/{job_id}` intercepted `/jobs/saved`; serialization referenced nonexistent salary/skill attributes. | Register static routes first and return existing fields. |
| User history | Queries referenced `match_score`, but the model stores `similarity_score`. | Query the actual column while keeping the response contract. |
| Analysis | API read `processed_text`, absent from Resume; skill percentages counted all candidate skills. | Read `raw_text`/stored skills and calculate actual overlap. |
| Score failures | Model errors silently became 15 semantic points. | Fail visibly instead of generating an artificial score. |
| Authorization | Any caller could write job records; scraper endpoints treated every signed-in account as an administrator. | Add configured administrator authorization and reject inactive accounts. |
| Sessions/config | Committed fallback JWT key, invalid example CORS format, working-directory-dependent `.env`, and implicit driver selection could break setup. | Validate production secrets, use backend-relative configuration, JSON array examples and an explicit psycopg2 driver. |
| Frontend auth | Consumers expected a token absent from AuthContext; the upload client sent none. | Expose validated token state and attach it to resume/matching requests. |
| Frontend URLs | Hardcoded localhost and undefined environment strings were mixed across pages. | Share one API base URL with a local fallback. |
| Frontend integration | Missing theme property, unstable provider mounting, incomplete analysis request and incompatible response shapes. | Align contexts, pass the selected resume ID and render the actual API analysis response. |
| Styling/build | PostCSS configuration was missing and explicitly ignored by Git. | Track the Tailwind/PostCSS config and verify compiled output. |
| Dependencies | The original npm install reported 20 vulnerabilities, including a critical Next.js advisory. | Upgrade Next.js/React, align lint tooling, refresh the lockfile and audit the result. |
| Embeddings | Every service constructed another model at import time; unrelated TensorFlow/Keras packages could break PyTorch inference. | Lazily share one cached model and select the PyTorch backend. |
| Ingestion | HTML reached embeddings, refreshed descriptions retained stale vectors/expiration, and failures could look like empty success. | Clean text, refresh embeddings/metadata, expose errors and remove the unimplemented Adzuna placeholder from runnable sources. |
| Request execution | Synchronous database calls were declared as async routes and could block the event loop. | Use synchronous FastAPI handlers so blocking work runs in the thread pool. |
| Background tasks | A background scraper reused the request's database session. | Give each run its own session, expose run state and reject overlapping runs in the same process. |
| Record deletion | Saved/application references could prevent deleting jobs or resumes. | Explicitly clean related job records and detach application resume references. |
| Seeding/migration | Repeated seeds duplicated records; extra jobs lacked embeddings; legacy auth assigned a shared password. | Skip existing seed pairs, embed additional records, label sample sources and disable unhashed legacy accounts and the earlier shared-password hash. |
| Repository hygiene | Generated Python bytecode was tracked. | Remove bytecode from tracking and keep local caches/build artifacts ignored. |

## Checks executed

- 27 backend tests passed against a temporary SQLite database with controlled embeddings.
- The same 27 tests passed against isolated PostgreSQL 18 with real Transformer embeddings enabled in route workflows. Calculation/failure unit tests intentionally retain their own controlled inputs.
- Frontend lint, TypeScript checking and the Next.js production build passed.
- `npm audit` reported zero known vulnerabilities after updating dependencies.
- One Playwright workflow passed in Microsoft Edge using real API calls, PDF parsing and Transformer embeddings: registration, upload, ranking, full analysis, bookmarking, application tracking, session restoration and theme persistence. This covers one desktop path, not every browser or screen size.
- All three PostgreSQL migration scripts completed twice on the disposable database, checking rerun behavior.

The first hosted backend check passed. The first hosted frontend check exposed missing optional platform dependencies in the Windows-generated npm lockfile. The lockfile was regenerated in an empty directory with the runner's npm version to restore clean Linux installation.

These are application-correctness and integration checks, not ranking-quality evidence. GitHub Actions configuration was added; local results do not imply a completed hosted CI run.

Real model inference was also executed with `all-MiniLM-L6-v2`: vectors had 384 dimensions. A software-role pair had cosine similarity 0.453418, versus 0.128016 for software development versus cooking. This is a smoke check on three short inputs, not a benchmark.

A live RemoteOK request returned two listings, with text cleaned of HTML and source URLs preserved. No Adzuna access was tested or claimed. External source availability can change.

## Work that would make the project stronger

1. **Measure retrieval quality.** Build a consented, anonymized set of resumes and relevance judgments. Compare semantic ranking with BM25/TF-IDF and a hybrid ranker. Report nDCG@k, recall@k, failure cases and latency. Keep evaluation data separate from tuning examples.
2. **Cover the whole document.** Test section-aware or chunked embeddings against the current truncated representation. Preserve all job descriptions rather than cutting them to 2,000 characters. Evaluate the accuracy/latency tradeoff before choosing a replacement.
3. **Normalize skills.** Add a reviewed alias map and distinguish exact matches, aliases and related skills. Fixed vocabulary extraction currently misses tools and can confuse broad terms. Test experience extraction separately from matching.
4. **Make ingestion durable.** Add an external worker queue, scheduled runs, retry/backoff, per-source rate policies and durable run history. Add database uniqueness for source/source-job-ID through a real migration; the current lock only prevents overlapping runs within one process.
5. **Prepare public deployment.** Use HttpOnly server sessions, login throttling, account verification/recovery, HTTPS, proxy upload limits and a documented retention policy. Add concurrent duplicate-write handling and versioned migrations. These features are not implied by passing local tests.
6. **Scale only when measured.** Batch embeddings, store model/version metadata, and introduce a vector index when catalog size justifies it. A model change must invalidate or rebuild stored embeddings.
7. **Expand browser coverage.** The automated desktop workflow covers registration, upload, analysis, bookmarks and application tracking. Add mobile layouts, other browser engines, application status editing, expired sessions, slow requests and concurrent-user cases.

The highest-value next step is the retrieval evaluation: it would let the project make defensible claims about recommendation quality rather than relying on screenshots or a cosine percentage.
