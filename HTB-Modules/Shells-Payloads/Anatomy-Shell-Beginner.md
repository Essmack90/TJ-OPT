---
tags: [module/shells-payloads, shell-anatomy, terminal-emulator, command-interpreter, bash, powershell, level/beginner]
---

# Anatomy of a Shell - Beginner's Guide

## What is a Shell?

A shell is a program that provides an interface to interact with the operating system. It accepts commands, interprets them, and passes them to the OS for execution.

**Think of it as:** The middle layer between you and the computer's kernel.

---

## The Three Components

User → Terminal Emulator → Command Language Interpreter → Operating System

| Component | Role |
|-----------|------|
| Terminal Emulator | The window/application you type into |
| Command Language Interpreter | The shell (Bash, PowerShell, etc.) |
| Operating System | Executes the commands |

---

## Terminal Emulators

A terminal emulator is the application that provides a window for you to interact with the shell.

### Common Terminal Emulators

| Terminal Emulator | Operating System |
|-------------------|------------------|
| Windows Terminal | Windows |
| cmder | Windows |
| PuTTY | Windows |
| kitty | Windows, Linux, MacOS |
| Alacritty | Windows, Linux, MacOS |
| xterm | Linux |
| GNOME Terminal | Linux |
| MATE Terminal | Linux |
| Konsole | Linux |
| Terminal | MacOS |
| iTerm2 | MacOS |

**Note:** Choosing a terminal emulator is personal preference. Don't let anyone make you feel bad for your choice.

---

## Command Language Interpreters

A command language interpreter (CLI) translates your typed commands into instructions the OS can execute.

### Common Shells / Interpreters

| Shell | Operating System | Default Prompt |
|-------|------------------|----------------|
| Bash | Linux, MacOS | $ |
| Zsh | Linux, MacOS | % or $ |
| PowerShell | Windows, Linux, MacOS | PS> |
| cmd.exe | Windows | > |
| sh | Linux/Unix | $ |

---

## Identifying Which Shell You're In

### Method 1: Look at the Prompt

- $ - Usually Bash, sh, or similar
- # - Root user in Bash
- PS> - PowerShell
- > - cmd.exe (Windows)

### Method 2: Use ps Command (Linux/Mac)

ps

Output:
    PID TTY          TIME CMD
   4232 pts/1    00:00:00 bash
  11435 pts/1    00:00:00 ps

The CMD column shows which shell is running.

### Method 3: Check Environment Variables (Linux/Mac)

env | grep SHELL

Output:
SHELL=/bin/bash

### Method 4: Check $PSVersionTable (PowerShell)

$PSVersionTable

---

## Hands-on in Pwnbox

### Opening the MATE Terminal

Click the green square icon at the top of the Pwnbox screen. This opens the MATE terminal emulator.

Try typing something random:

wasdf

Output:
bash: wasdf: command not found

**What we learn:** The $ prompt and "bash: command not found" tells us we're in Bash.

### Check with ps

ps

Output:
    PID TTY          TIME CMD
   4232 pts/1    00:00:00 bash
  11435 pts/1    00:00:00 ps

Confirmed: Bash.

### Check with env

env | grep SHELL

Output:
SHELL=/bin/bash

---

## PowerShell in Pwnbox

### Opening PowerShell

Click the blue square icon at the top of the Pwnbox screen. This opens the MATE terminal running PowerShell instead of Bash.

### Compare Bash and PowerShell

| Feature | Bash | PowerShell |
|---------|------|------------|
| Prompt | $ | PS> |
| Command | ls | Get-ChildItem or ls |
| Help | man ls | Get-Help Get-ChildItem |
| Aliases | Many built-in | Many built-in |
| Case-sensitive | Yes | No |

### Try the same commands in both

**In Bash:**
ls -la
echo "Hello"
ps

**In PowerShell:**
ls -la
echo "Hello"
ps

Notice the differences in output and which commands are recognized.

---

## Why This Matters for Pentesters

| Reason | Why |
|--------|-----|
| Command compatibility | Bash commands won't work in PowerShell |
| Scripting | Different syntax for automation |
| Exploitation | Payloads must match the target shell |
| Persistence | Different methods for different shells |
| Detection | Shell activity looks different per platform |

**The Rule:** Know what shell you're in before you start typing.

---

## Key Takeaways

- A shell requires three components: terminal + interpreter + OS
- Terminal emulator is just the window - the shell is the interpreter
- Bash uses $ prompt, PowerShell uses PS>
- Use ps, env, or $PSVersionTable to identify your shell
- The same terminal can run different shells
- Pwnbox has both Bash and PowerShell - practice in both
- Commands that work in one shell may fail in another
- Know your target's default shell (Linux = Bash, Windows = cmd/PowerShell)
- Shell identification is the first step in any engagement
- Practice until you can spot the difference instantly
