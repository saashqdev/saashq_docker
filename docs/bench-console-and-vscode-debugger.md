Add the following configuration to `launch.json` `configurations` array to start wrench console and use debugger. Replace `development.localhost` with appropriate site. Also replace `saashq-wrench` with name of the wrench directory.

```json
{
  "name": "Wrench Console",
  "type": "python",
  "request": "launch",
  "program": "${workspaceFolder}/saashq-wrench/apps/saashq/saashq/utils/wrench_helper.py",
  "args": ["saashq", "--site", "development.localhost", "console"],
  "pythonPath": "${workspaceFolder}/saashq-wrench/env/bin/python",
  "cwd": "${workspaceFolder}/saashq-wrench/sites",
  "env": {
    "DEV_SERVER": "1"
  }
}
```
