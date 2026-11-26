# Stories

Put each user story here as `US-<number>.docx`, `.txt` or `.md` (for example `US-107.docx`). Copy `TEMPLATE.txt` to start one.

Run it:

- Claude Code: `/sdlc stories/US-107.docx`
- Copilot: tell SDLC Orchestrator "The story is in stories/US-107.docx"
- CodeMie: `python3 scripts/story/read_story.py stories/US-107.docx --copy`, then paste into the chat

Each story needs the story ID on the first line, a role/goal/benefit sentence, exact strings and values spelled out, and numbered acceptance criteria. The agents copy exact text verbatim, so typos in the story become typos in the code. Word tables are read as `a | b` rows; images are not read.

The pipeline copies the approved story into `requirements.md`; the file here stays the original.
