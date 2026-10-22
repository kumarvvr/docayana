# tools/utilities

Small standalone helpers for working on docayana. They need no credentials and touch no infrastructure.

## Tools
- `node_id.py`: prints random node ids in git commit-id style (lowercase hex, 40 characters by default).
  Run from the repo root: `.\env\Scripts\python.exe tools\utilities\node_id.py -n 5`
  Use `--length 20` for shorter ids (80 random bits, still safe for billions of nodes).
  Import it with `from node_id import new_node_id` when the folder is on the path.
