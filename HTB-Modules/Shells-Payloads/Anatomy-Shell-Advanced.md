---
tags: [module/shells-payloads, shell-anatomy, terminal-emulator, command-interpreter, bash, powershell, process-analysis, level/advanced, practical]
---

# Anatomy of a Shell - Practical Application

## Complete Shell Anatomy Workflow

Phase 1: Terminal Emulator Identification
Phase 2: Shell Detection Techniques
Phase 3: Process Analysis
Phase 4: Environment Variable Analysis
Phase 5: Cross-Platform Shell Differences
Phase 6: Shell Customization
Phase 7: Automation

---

## Phase 1: Terminal Emulator Identification

### Identifying Terminal on Linux

# Check parent process
ps -ef | grep $$

# Check terminal type
echo $TERM

# Check terminal process
pstree -s $$

### Identifying Terminal on Windows

# Check process tree
Get-Process -Id $pid | Format-List *

# Check console host
Get-WmiObject Win32_Process | Where-Object { $_.ProcessId -eq $pid }

---

## Phase 2: Shell Detection Techniques

### Linux Shell Detection

# Check current shell
echo $0
ps -p $$

# List available shells
cat /etc/shells

# Check user's default shell
grep $(whoami) /etc/passwd | cut -d: -f7

# Check running shells
ps aux | grep -E "bash|zsh|sh|dash|fish"

### Windows Shell Detection

# Check PowerShell version
$PSVersionTable

# Check if running in PowerShell vs cmd
Get-Process -Id $pid | Select-Object ProcessName

# Check execution policy
Get-ExecutionPolicy

# Check PowerShell edition
$PSVersionTable.PSEdition

### PowerShell vs cmd Detection

# This command works in PowerShell, fails in cmd
Get-ChildItem

# This command works in cmd, works differently in PowerShell
dir

# Check parent process
(Get-Process -Id $pid).Parent

---

## Phase 3: Process Analysis

### Linux Process Tree Analysis

# Full process tree
pstree -pa

# Show shell hierarchy
ps -e -o pid,ppid,cmd | grep -E "bash|zsh|sh|sshd"

# Check all terminals
ps aux | grep -E "bash|zsh|sh" | grep -v grep

# Check network connections from shell
lsof -p $$ | grep ESTABLISHED

### Windows Process Analysis

# Check process tree
Get-Process | Where-Object { $_.ProcessName -match "powershell|cmd" }

# Check parent-child relationships
Get-WmiObject Win32_Process | Where-Object { $_.Name -match "powershell|cmd" } | 
    Select-Object ProcessId, Name, ParentProcessId

# Check for hidden processes
Get-Process -IncludeHidden

### Detecting Shells from Network Connections

# Linux
netstat -antp | grep ESTABLISHED

# Windows
netstat -ano | findstr ESTABLISHED

---

## Phase 4: Environment Variable Analysis

### Linux Environment Variables

# Show all environment variables
env

# Show shell-specific variables
set

# Show shell options
echo $-

# Show shell version
echo $BASH_VERSION
echo $ZSH_VERSION
echo $PS1

### Windows Environment Variables

# Show all environment variables
Get-ChildItem Env:

# Show PowerShell-specific variables
$PSVersionTable
$Host
$ExecutionContext.SessionState.LanguageMode

# Show cmd variables (from PowerShell)
cmd /c set

### Interesting Environment Variables

| Variable | Linux | Windows | Purpose |
|----------|-------|---------|---------|
| PATH | ✅ | ✅ | Command search paths |
| HOME | ✅ | ✅ | User home directory |
| USER | ✅ | ✅ | Current username |
| SHELL | ✅ | ❌ | Default shell path |
| PS1 | ✅ | ❌ | Prompt string |
| PROMPT | ❌ | ✅ | cmd prompt |
| PWD | ✅ | ✅ | Current directory |

---

## Phase 5: Cross-Platform Shell Differences

### Command Comparison

| Operation | Bash | PowerShell | cmd |
|-----------|------|------------|-----|
| List files | ls | Get-ChildItem, ls | dir |
| Change dir | cd | Set-Location, cd | cd |
| Show file | cat | Get-Content, cat | type |
| Clear screen | clear | Clear-Host, cls | cls |
| Find processes | ps | Get-Process, ps | tasklist |
| Kill process | kill | Stop-Process, kill | taskkill |
| Network | netstat | Get-NetTCPConnection | netstat |
| Help | man command | Get-Help command | command /? |

### Case Sensitivity

# Bash (case-sensitive)
ls /home/user
LS /home/user  # Fails

# PowerShell (case-insensitive)
Get-ChildItem C:\Users
get-childitem c:\users  # Works

# cmd (case-insensitive)
DIR C:\Users
dir c:\users  # Works

### Path Separators

# Linux (forward slash)
ls /home/user/Documents

# Windows (backslash)
Get-ChildItem C:\Users\Documents

# PowerShell accepts both
Get-ChildItem C:/Users/Documents

---

## Phase 6: Shell Customization

### Linux Shell Customization

# Bash configuration files
~/.bashrc
~/.bash_profile
/etc/bash.bashrc

# Zsh configuration
~/.zshrc

# Custom prompt (Bash)
export PS1="\u@\h:\w\$ "

# Add aliases
alias ll='ls -la'
alias update='sudo apt update && sudo apt upgrade'

### Windows PowerShell Customization

# PowerShell profile location
$PROFILE

# Edit profile
notepad $PROFILE

# Custom prompt
function prompt {
    "$env:USERNAME@$env:COMPUTERNAME $(Get-Location)> "
}

# Add aliases
Set-Alias ll Get-ChildItem
Set-Alias gs git status

### Windows cmd Customization

# Registry settings
HKEY_CURRENT_USER\Software\Microsoft\Command Processor

# AutoRun commands
reg add "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d "doskey ls=dir $*"

---

## Phase 7: Automation

### Shell Detection Script (Linux)

Save as detect-shell.sh:

#!/bin/bash

echo "=== Shell Detection ==="
echo "Current shell: $0"
echo "Shell PID: $$"
echo "Parent process: $(ps -o comm= -p $PPID)"

echo -e "\n=== Process Info ==="
ps -p $$ -o pid,ppid,cmd

echo -e "\n=== Environment ==="
echo "SHELL: $SHELL"
echo "BASH_VERSION: $BASH_VERSION"
echo "ZSH_VERSION: $ZSH_VERSION"
echo "USER: $USER"
echo "HOME: $HOME"
echo "PATH: $PATH"

echo -e "\n=== Available Shells ==="
cat /etc/shells 2>/dev/null || echo "Cannot read /etc/shells"

### Shell Detection Script (PowerShell)

Save as Detect-Shell.ps1:

Write-Host "=== Shell Detection ===" -ForegroundColor Green
Write-Host "Process: $((Get-Process -Id $pid).ProcessName)"
Write-Host "PID: $pid"
Write-Host "Parent PID: $((Get-CimInstance Win32_Process -Filter "ProcessId=$pid").ParentProcessId)"

Write-Host "`n=== PowerShell Info ===" -ForegroundColor Green
Write-Host "Version: $($PSVersionTable.PSVersion)"
Write-Host "Edition: $($PSVersionTable.PSEdition)"
Write-Host "Language Mode: $($ExecutionContext.SessionState.LanguageMode)"
Write-Host "Execution Policy: $(Get-ExecutionPolicy)"

Write-Host "`n=== Environment ===" -ForegroundColor Green
Write-Host "User: $env:USERNAME"
Write-Host "Computer: $env:COMPUTERNAME"
Write-Host "OS: $env:OS"
Write-Host "Path: $env:PATH"

### Remote Shell Detection

# Detect shell on remote Linux
ssh user@target "ps -p $$ -o comm="

# Detect shell on remote Windows (WinRM)
Invoke-Command -ComputerName TARGET -ScriptBlock { $PSVersionTable }

---

## Anatomy of a Shell Cheatsheet

| Task | Linux Command | Windows Command |
|------|---------------|-----------------|
| Check current shell | echo $0 | $PSVersionTable |
| Check PID | echo $$ | $pid |
| List processes | ps aux | Get-Process |
| Environment vars | env | Get-ChildItem Env: |
| Check PATH | echo $PATH | $env:PATH |
| Check shell version | $BASH_VERSION | $PSVersionTable.PSVersion |
| List available shells | cat /etc/shells | (not applicable) |
| Check parent process | ps -o ppid= -p $$ | (Get-Process -Id $pid).Parent |

---

## Key Takeaways

- Terminal emulator is just the window - the shell is the interpreter
- Bash uses `$`, PowerShell uses `PS>`, cmd uses `>`
- Use `ps`, `env`, or `$PSVersionTable` to identify your shell
- Same terminal can run different shells
- Commands are not cross-platform - know your target
- PowerShell is case-insensitive, Bash is case-sensitive
- Shell customization affects your workflow
- Process analysis reveals shell hierarchy
- Environment variables store critical information
- Remote shell detection requires different techniques
- Practice in both Bash and PowerShell until fluent
- Shell identification is the first step in any engagement
- The more you know about shells, the better you'll be at exploiting them
