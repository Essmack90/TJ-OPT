# File Upload Attacks — Command Appendix

Part of [[COMMAND APPENDIX]]. Filter bypass tricks for getting an executable (or traversal-able) file past an upload form.

---

## File Upload Filter Bypasses

- Case-swap the extension: `.php` → `.pHP`
- Alternate/legacy extensions: `.phps`, `.php7`
- Upload as an innocuous type (`.txt`) first, then use the app's own rename feature to restore the executable extension
- Check whether the `filename` field itself is traversal-able, even if the uploaded content can't execute (overwrite `authorized_keys` instead)

See [[Common Web Application Attacks#9.3.1. Using Executable Files|9.3.1]], [[Common Web Application Attacks#9.3.2. Using Non-Executable Files|9.3.2]].

#### Tags: #FileUpload #ExtensionFilterBypass

---

## **Outstanding**
This area grows alongside the modules. Whenever a new upload-bypass trick comes up (magic-byte/MIME spoofing, double extensions, null-byte tricks, polyglot files, etc), add it here with a link back to the source section.
