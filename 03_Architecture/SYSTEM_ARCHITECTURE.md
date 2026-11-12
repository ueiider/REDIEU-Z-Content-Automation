# System Architecture

## Intended workflow

1. Discover GTA 6 content opportunities.
2. Collect source links and available metadata.
3. Analyse transcripts and source evidence.
4. Rank topics by relevance, freshness and audience interest.
5. Generate original scripts using Nemotron.
6. Generate narration using the configured TTS engine.
7. Select relevant original or licensed footage.
8. Generate captions and synchronise them with audio.
9. Render vertical video.
10. Run quality checks.
11. Generate platform metadata.
12. Save to review queue.
13. Obtain human approval.
14. Dispatch to selected platforms.
15. Record publication URLs and status.

## Components

### Research
- YouTube discovery.
- yt-dlp metadata and permitted transcript extraction.
- Official Rockstar sources.
- News sources.
- Free/licensed media libraries.

### AI
- OpenCode.
- Ollama.
- Nemotron.
- Other locally available models after evaluation.

### Production
- PurffleShorts.
- MoneyPrinterTurbo.
- FFmpeg.
- Edge TTS.
- Existing Python pipeline.

### Publishing
- Open-Dispatch.
- YouTube Data API.
- Instagram publishing integration.
- TikTok publishing integration.
- Facebook publishing integration.

## Important separation

Research, script generation, video rendering and publishing should be separate stages.

A failed publishing action must not destroy a rendered video.

A rendering failure must not delete the source script.

Each asset should have a persistent identifier and status.
