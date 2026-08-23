# Twine

#CICD #DependencyConfusion #PyPI #Python

Python package upload utility. Used to publish packages to PyPI or any private package index (like `pypi.offseclab.io`).

**Installed via:** `pip install twine --break-system-packages` (when apt repos are unavailable)
**Binary location after pip install:** `~/.local/bin/twine`

---

## Usage

```bash
# Upload a package to a private registry
~/.local/bin/twine upload \
  --repository-url http://pypi.offseclab.io/ \
  -u <username> -p <password> \
  dist/mypackage-1.1.4.tar.gz

# Check the upload succeeded
curl -u '<user>:<pass>' http://pypi.offseclab.io/<package-name>/json

# Remove a package version
curl -u "<user>:<password>" \
  --form ":action=remove_pkg" \
  --form "name=<package-name>" \
  --form "version=<version>" \
  http://pypi.offseclab.io/
```

---

## OSCP Use Case

Dependency Chain Abuse (CICD-SEC-3). Upload a malicious version of an internal package to a private PyPI server at a higher version number than the currently installed one. The production build system installs the highest available version, executing your payload on import.

> 🔧 Technique: Always upload by specific filename (`dist/mypackage-1.1.4.tar.gz`) instead of `dist/*`. Old tarballs from previous lab sessions bake in stale LHOST values. pip picks the HIGHEST version regardless of upload order, so a stale `1.1.6` beats a fresh `1.1.4`.

See [[26. Attacking AWS Cloud Infrastructure#26.9.6 Publishing the Malicious Package|Attacking AWS Cloud Infrastructure#26.9.6 Publishing the Malicious Package]] for full context.

**Offsec module:** [[26. Attacking AWS Cloud Infrastructure|Attacking AWS Cloud Infrastructure]] (Module 26)
