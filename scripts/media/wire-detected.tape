# wire-detected.tape — the recommended MCP door in ~25 seconds: preview the
# clients this machine shows, wire them, run it again to see nothing move,
# then read one file to see the existing server kept. Every command is the
# released binary's own; scripts/media/render.sh stages the sandbox HOME
# (/tmp/you: Cursor and Claude Code settings, a project with a VS Code MCP
# file) and writes the shell.zsh sourced below. Nothing global is touched.
# House theme = the engine's nika-hero palette.
Output wire-detected.gif

Set Shell zsh
Set FontFamily "JetBrains Mono"
Set FontSize 21
Set Width 1420
Set Height 780
Set Padding 24
Set Margin 22
Set MarginFill "#4f86ff"
Set BorderRadius 14
Set WindowBar Colorful
Set WindowBarSize 42
Set Theme { "name": "nika", "background": "#08090b", "foreground": "#dbe3ee", "cursor": "#4f86ff", "black": "#10131a", "red": "#ff6b6b", "green": "#34d399", "yellow": "#f0b45b", "blue": "#4f86ff", "magenta": "#b07bff", "cyan": "#22d3ee", "white": "#dbe3ee", "brightBlack": "#5b6472", "brightRed": "#ff8f8f", "brightGreen": "#5ee6b0", "brightYellow": "#ffd08a", "brightBlue": "#8db4ff", "brightMagenta": "#c9a2ff", "brightCyan": "#67e3f5", "brightWhite": "#ffffff" }
Set TypingSpeed 30ms
Set PlaybackSpeed 1.0

Hide
Type ". /tmp/you/shell.zsh && clear"
Enter
Show

Type "# Cursor, Claude Code and a VS Code project on this machine · preview first"
Enter
Sleep 600ms
Type "nika wire detected --dry-run"
Enter
Sleep 3200ms

Type "# then wire them"
Enter
Sleep 500ms
Type "nika wire detected"
Enter
Sleep 2800ms

Type "# again: already current, nothing moves"
Enter
Sleep 500ms
Type "nika wire detected"
Enter
Sleep 3800ms

Type "clear"
Enter
Type "# Cursor kept the server it already had"
Enter
Sleep 500ms
Type "cat ~/.cursor/mcp.json"
Enter
Sleep 4200ms
Sleep 1200ms
