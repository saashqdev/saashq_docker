Add the following configuration to `launch.json` `configurations` array to start bench console and use debugger. Replace `development.localhost` with appropriate site. Also replace `saashq-bench` with name of the bench directory.

```json
{
  "name": "Bench Console",
  "type": "python",
  "request": "launch",
  "program": "${workspaceFolder}/saashq-bench/apps/saashq/saashq/utils/bench_helper.py",
  "args": ["saashq", "--site", "development.localhost", "console"],
  "pythonPath": "${workspaceFolder}/saashq-bench/env/bin/python",
  "cwd": "${workspaceFolder}/saashq-bench/sites",
  "env": {
    "DEV_SERVER": "1"
  }
}
```
