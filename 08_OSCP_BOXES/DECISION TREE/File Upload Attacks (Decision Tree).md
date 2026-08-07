# File Upload Attacks, Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" for file upload forms.

---

### Found an upload form
→ Try uploading a webshell (`.php`) directly first
→ Blocked? Try a case-swapped extension (`.pHP`), or `.phps`/`.php7`, or upload as `.txt` then rename via the app's own rename feature
→ IIS/ASP.NET target instead of PHP? Same idea, `/usr/share/webshells/aspx/cmdasp.aspx`, upload via the browser (viewstate tokens are painful with curl)
→ Upload lands on a different port/path than where it's served from? Check the app's own text/behavior for clues about where uploads actually go
→ See [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]] and [[Common Web Application Attacks#9.4.1. OS Command Injection|9.4.1 case study 4]]

### Upload form works but nothing you upload ever executes
→ Check whether the `filename` field itself is traversal-able. If so, overwrite something like `authorized_keys` instead of relying on execution
→ See [[Common Web Application Attacks#9.3.2. Using Non-Executable Files|9.3.2]]
