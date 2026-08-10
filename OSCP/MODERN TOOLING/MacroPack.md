# macro_pack

Payload-generation and obfuscation tool for Office macros, VBS, shortcuts, and other script-based lure formats. **This generates payloads, it doesn't deliver or exploit anything itself**, the delivery/pretext/trigger side of a client-side attack still has to be done exactly as the module teaches.

---

## What it replaces, and why it's faster

[[Client-Side Attacks#12.2.3. Leveraging Microsoft Word Macros|12.2.3]] builds the VBA macro by hand: writing `AutoOpen`/`Document_Open`/`MyMacro`, generating a base64 UTF-16LE download cradle via `pwsh`, then mechanically chunking it into ≤255-character `Str = Str + "..."` lines with a small Python script (all genuinely worth knowing how to do by hand at least once, that's the whole point of the manual walkthrough). `macro_pack` automates that same generation-and-chunking process, plus adds obfuscation (variable/function renaming, string splitting) aimed specifically at dodging static AV signatures, something the manual approach doesn't attempt at all.

## Install

```bash
git clone https://github.com/sevagas/macro_pack.git
cd macro_pack
pip3 install -r requirements.txt
```

## Usage

```bash
# Generate a macro-enabled document from a payload one-liner
python3 macro_pack.py -G output.doc -o -f payload.txt

# -o enables obfuscation, -G specifies the output document format/name
# payload.txt would contain the same kind of PowerShell download-cradle one-liner used in 12.2.3

# macro_pack can also take input from stdin, useful for chaining with another payload generator
echo "<VBA or PowerShell payload>" | python3 macro_pack.py -G output.docm -o
```
*Compatible with payloads from Metasploit/Empire-style generators as input, but `macro_pack` itself is just the document-packaging and obfuscation step, not an exploitation framework. Still worth building the macro by hand at least once (per 12.2.3) to actually understand what's happening before reaching for a generator that does it in one command.*

## Where this applies in the vault

- [[Client-Side Attacks#12.2.3. Leveraging Microsoft Word Macros|12.2.3, Leveraging Microsoft Word Macros]], as a faster path to the same `.doc`/`.docm` macro artifact once the manual technique (and its `.doc`-vs-`.docx` gotcha) is actually understood

#### Tags: #ModernTooling #MacroPack #WordMacros #PayloadGeneration #ClientSideAttacks
