# PurffleShorts and Existing Pipeline

## Purpose
Retain the existing Shorts generation pipeline and improve it incrementally.

## Known components
- Python scripts.
- JSON script definitions.
- JSON production queue.
- Background worker.
- ctl.py management interface.
- FFmpeg.
- Edge TTS.
- Animated captions.
- REDIEU Z watermark.

## Management commands

```powershell
python D:\GTA6_Content\Pipeline\ctl.py status

python D:\GTA6_Content\Pipeline\ctl.py stop

python D:\GTA6_Content\Pipeline\ctl.py start
```

Verify the actual supported commands from ctl.py before using commands not listed above.

## Output
`D:\GTA6_Content\03_Shorts\Ready_For_Review`

## Known queue state
Shorts 002–008 were completed in the observed run. Short 009 was pending.

## Improvements required

1. Use footage that directly corresponds to the narration.
2. Add a source-to-scene mapping.
3. Support multiple gameplay sources.
4. Improve background music selection and mixing.
5. Keep captions synchronised.
6. Improve watermark placement.
7. Maintain title, description and hashtag JSON.
8. Validate audio and video before marking an item complete.

## Do not

- Recreate working pipeline components unnecessarily.
- Replace existing scripts without inspecting them.
- Delete completed videos.
- Publish trailer footage without confirming rights.
