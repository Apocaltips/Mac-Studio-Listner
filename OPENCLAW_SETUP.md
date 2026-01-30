# OpenClaw Setup

This project includes a skill at `skills/office-recorder/SKILL.md` that calls the local control script via the OpenClaw Exec tool.

## 1) Install the skill
- Copy the `skills/office-recorder` folder into your OpenClaw skills directory, or point OpenClaw at this repo.

## 2) Allow the control script
OpenClaw Exec must be allowed to run the script. Add the script to your allowlist (see OpenClaw Exec approvals).

Recommended allowlist entry:

```
/Users/<you>/Mac-Studio-Listner/scripts/office_recorder_ctl.sh
```

## 3) Use it

Text OpenClaw:
- "start recording"
- "stop recording"
- "status"
- "summarize"
- "pipeline"
- "schedule status"

Or use the slash command:

```
/skill office-recorder start
```
