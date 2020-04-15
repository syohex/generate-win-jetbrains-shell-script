# Generate JetBrains IDE shell script for Windows

JetBrains ToolBox has feature which generates launch script. However it supports only batch script on Windows, and the scripts does not work well on Git bash.
This scripts generates JetBrains IDE shell scripts for Git Bash

## Example

```bash
# Generate IDE launch scripts into ~/bin
python generate-win-jetbrains-shell-script.py ~/bin
```