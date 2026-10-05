# Async video lifecycle

`seedance-2.5` uses `/v1/videos/generations`. Treat video creation as a job lifecycle:

1. Validate the prompt and model-specific fields against the [Argolink model page](https://argolink.io/gh-seedance-2-5-prompt-playbook).
2. Submit once and persist the returned task ID.
3. Poll `GET /v1/tasks/{id}` with bounded backoff.
4. Stop on a terminal state, then download the returned media URL before its retention window ends.

## Current catalog note

4–30 seconds; 480p, 720p or 1080p; one output per request; reference videos add their seconds to the billed seconds; edits videos of 4–30 seconds

A timeout leaves the task outcome unknown. Query the task status before considering a retry. Never hide a failed terminal state by returning a fabricated media URL.
