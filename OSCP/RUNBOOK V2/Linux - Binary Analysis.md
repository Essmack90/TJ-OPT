# Linux - Binary Analysis

**Step 7B of 50 · Linux**

*Analyse a downloaded executable locally before spending fragile requests against the target service.*

## When to use this page

Use this branch when web enumeration exposes a server, client, archive, or other executable. Treat the file as loot: record its type, preserve the original, and perform crash analysis locally first.

## Run this

> **Why:** These checks identify the binary format and useful metadata before debugging. A 32-bit PE custom server commonly runs under Wine, while an ELF should be analysed with native Linux tooling.
```bash
mkdir -p "$BoxDir/loot/binary-analysis"
cp "$BoxDir/loot/$File" "$BoxDir/loot/binary-analysis/$File.original"
file "$BoxDir/loot/$File"
strings -a -n 5 "$BoxDir/loot/$File" | tee "$BoxDir/loot/binary-analysis/strings.txt"
```

For an ELF, continue with native metadata and hardening checks:

```bash
readelf -h -l -s "$BoxDir/loot/$File"
checksec --file="$BoxDir/loot/$File"
```

For a 32-bit PE custom server, inspect it under Wine and record the image base:

```bash
wine "$BoxDir/loot/$File"
objdump -p "$BoxDir/loot/$File" | grep -i ImageBase
```

## Crash and offset workflow

> **Why:** A local crash gives the exact saved-instruction-pointer offset without consuming the target’s one-shot service. Confirm control before building a payload.
```bash
msf-pattern_create -l $PatternLength > "$BoxDir/loot/binary-analysis/pattern.txt"
# Send the pattern to the local test instance, then record the crashed EIP/RIP.
msf-pattern_offset -l $PatternLength -q $EipValue
```

After control is confirmed, test bad characters, then find a stack redirection gadget in the target binary:

```bash
ROPgadget --binary "$BoxDir/loot/$File" | grep -E 'push esp ; ret$|call esp ; ret$|jmp esp$'
```

> [!warning] 💡
> Prefer a gadget in the target executable. A system-DLL address may differ between the local Wine environment and the target; the target PE’s image base is the safer reference when the executable is non-ASLR.

## What did you get?

- [ ] A PE32 custom server is confirmed → **Run the crash/offset workflow locally, adapt the payload layout, then go to Step 10 · [[Linux - Exploit Search]] and Step 11 · [[Linux - RCE to Shell]]**
- [ ] EIP/RIP is not controlled → **Increase the pattern length, reproduce the crash locally, and recalculate the offset**
- [ ] A bad character corrupts the payload → **Remove it from the test set, regenerate the payload, and retest before sending remotely**
- [ ] A target-binary stack gadget is found → **Use the exact offset, gadget, terminator requirements, and a payload compatible with the target architecture**
- [ ] The file is an ELF rather than a PE → **Use `checksec`, symbols, and `readelf` output to choose the native analysis path; route confirmed memory corruption to Step 10 · [[Linux - Exploit Search]]**
- [ ] The downloaded file is not executable → **Read it as an archive, script, configuration, or client artifact and return to Step 5 · [[Linux - Web Enum]]**

## Notes

Keep the original binary unchanged and store patterns, debugger notes, hashes, and screenshots under private loot. Match the shellcode architecture to the process, and preserve required null-byte or line-ending behaviour from the service’s README.

## Gotcha

> [!warning] 💡
> Do not probe a fragile custom server repeatedly after a crash. Prepare the listener and payload first, send one controlled request after a reset, and treat a dead connection as evidence that the service needs reverting.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Dawn2|Dawn2]] -- analysed two leaked PE servers and calculated both overflow layouts

## Related stages

- [[Linux - Web Enum]]
- [[Linux - Exploit Search]]
- [[Linux - RCE to Shell]]
- [[Linux - Clean Down]]

## External Resources

- https://book.hacktricks.wiki/en/binary-exploitation/rop-return-oriented-programing/
- https://github.com/JonathanSalwan/ROPgadget
- https://www.revshells.com/

## Why this matters for OSCP

Offline binary analysis turns an unknown service into a reproducible exploit workflow and protects limited target interactions from avoidable guesses.
