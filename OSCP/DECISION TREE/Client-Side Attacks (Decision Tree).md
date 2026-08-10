# Client-Side Attacks, Decision Tree

Part of [[DECISION TREE]]. "I found X, what do I try" for getting a foothold on a target with nothing directly exposed. Distinct from [[Phishing (Decision Tree)|Phishing]] (that area covers website cloning/credential capture), this one covers macro and Windows-library-file delivery mechanics.

---

### Target is internal-only, no services worth attacking directly
→ Straight port-scan-and-exploit has nothing to reach. Switch to a client-side vector instead: recon the target org first ([[Client-Side Attacks#12.1. Target Reconnaissance|12.1]], document metadata + Canarytoken fingerprinting), then pick Office macros ([[Client-Side Attacks#12.2. Exploiting Microsoft Office|12.2]]) or Windows library files ([[Client-Side Attacks#12.3. Abusing Windows Library Files|12.3]]) based on what the recon told you about the target's OS/software.

### A freshly-saved macro doc doesn't fire on reopen (no security bar, no autorun, nothing happens)
→ Don't assume the macro is broken. Isolate payload-correctness first: **View → Macros → select the macro → Run**, if that catches a shell, the code itself is fine.
→ If it is fine, just try reopening the file again normally (double-click). Root cause is often a one-off UI/session glitch, not a real Trust Center block.
→ If it's consistently silent with genuinely no bar ever appearing, check **File → Options → Trust Center → Trust Center Settings → Macro Settings**, "Disable all macros without notification" blocks silently with no bar at all, different from the normal "with notification" default.
→ See [[Client-Side Attacks#🔁 Lab 1 Rebuild (fresh instance, after prior OFFICE VM corruption)|Lab 1 Rebuild troubleshooting]].

### Uploaded a macro-laden document to a target with a "simulated user" watcher script, listener's healthy, still nothing lands
→ **Check this first, it's the most likely cause and the cheapest to rule out: was the document actually saved as `.doc`/`.docm`, not `.docx`?** Office silently strips macros entirely on save to `.docx`, no error, no warning. A macro built and tested live in the same Word session still *looks* like it works (running from memory, not from the saved file), which is exactly what makes this so easy to miss. Verify with a genuine cold reopen (close Word fully, reopen from disk, watch the listener) before trusting any earlier "it worked" result.
→ If the format's confirmed correct and cold-reopen-tested, only then move to the network/infra checks: listener actually bound (`nc` shows `listening`, no bind error) → correct upload field name and exact required filename (check the task wording verbatim, don't assume) → DNS/IP actually resolving and connecting where you think (`getent hosts <name>`, `curl -v`)
→ **Caution: don't over-trust a plausible-sounding infra theory (e.g. "the watcher script must be one-shot") once the cheap checks pass, if the format issue is still lurking unverified.** Confirmed on this exact section: a one-shot-watcher theory was written up as the leading explanation after the network checks passed clean, but the real cause on a repeat attempt turned out to be the `.docx` mistake all along, made twice, undetected both times because the live-session test looked fine.
→ See [[Client-Side Attacks#Lab 2 (VM #2, TICKETS): delivering the macro to a simulated user|Lab 2 troubleshooting]] for the full elimination trail and the correction.

### A Windows library file (`.Library-ms`) worked once, but stops working after being reopened, restarted, or moved to another machine
→ Opening it the first time mutates the file: Windows rewrites the `url` tag from a plain `http://` address to a UNC path (`\\<ip>\DavWWWRoot`) and adds a `serialized` tag optimized for that specific machine's WebDAV client.
→ That mutated version may not work correctly elsewhere. Reset the file back to its original plain XML before redelivering it to a real target, every time it gets test-opened.
→ See [[Client-Side Attacks#Step 3: Test it, and handle the WebDAV self-rewrite gotcha|12.3.1, Step 3]].

### Worried a tech-savvy target will check where a `.lnk` shortcut actually points before running it
→ Windows only shows the first ~255 characters of a shortcut's target in the Properties window, but the real target field holds up to 4096.
→ Pad the malicious command with a delimiter plus a long, boring, benign-looking command, it pushes the real payload out of the visible area.
→ See [[Client-Side Attacks#Step 4: Build the `.lnk` shortcut payload (the actual reverse-shell trigger)|12.3.1, Step 4]].

#### Tags: #ClientSideAttacks #DecisionTree #WindowsLibraryFiles #WordMacros #WebDAV
