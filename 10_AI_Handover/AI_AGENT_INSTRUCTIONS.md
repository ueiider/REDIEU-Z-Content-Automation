# AI AGENT HANDOVER — REDIEU Z

You are taking over an existing local GTA 6 content automation project.

## Mandatory first actions

1. Read the root README.
2. Read PROJECT_HISTORY.md.
3. Read SYSTEM_ARCHITECTURE.md.
4. Read TOOL_INVENTORY.md.
5. Read OPEN_DISPATCH.md.
6. Read YOUTUBE_OAUTH.md.
7. Read ROADMAP.md.
8. Inspect the actual local installation.

## Local root

`D:\GTA6_Content`

## User's preferred AI environment

OpenCode with Nemotron through Ollama.

Do not assume Claude is available or required.

## Operating rules

- Work autonomously within the explicitly authorised scope.
- Prefer one focused change at a time.
- Avoid unnecessary installations.
- Avoid paid APIs unless explicitly approved.
- Preserve working components.
- Never modify unrelated projects.
- Do not terminate the Revit MCP service on port 8000.
- Open-Dispatch was observed on port 8001.
- Do not overwrite existing videos.
- Do not delete existing queue entries.
- Do not expose secrets.
- Do not publish without explicit approval.

## Before modifying code

Inspect:
- Current branch.
- Git status.
- Existing implementation.
- Configuration.
- Logs.
- Existing outputs.

Make a backup before destructive modifications.

## Production quality

A video is not ready merely because FFmpeg produced an MP4.

Verify that:
- Narration and visuals match.
- Facts are supported.
- Rumours are labelled.
- Captions are synchronised.
- Audio is clear.
- Music is licensed.
- Watermark is correctly positioned.
- Metadata is present.

## Reporting format

At the end of each task report:

1. Completed work.
2. Files changed.
3. Tests performed.
4. Test results.
5. Remaining blockers.
6. Next recommended action.

## Documentation maintenance

Update the relevant documentation whenever a tool is installed, configured, modified or successfully tested.

Maintain CURRENT_STATUS.md with the latest verified state.

Do not convert an assumption into a confirmed fact.
