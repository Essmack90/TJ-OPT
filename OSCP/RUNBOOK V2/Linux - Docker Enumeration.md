# Linux - Docker Enumeration

**Step 13C of 50 · Linux**

Inspect Docker containers and container-aware wrapper scripts after a foothold. Route exposed environment values to [[Linux - Credential Search]] and exact sudo rules to [[Linux - Sudo Check]].

## Run this

Start with identity, group membership, the runtime, loopback listeners, and all containers:

```bash
id
getent group docker
command -v docker
docker ps -a 2>/dev/null
ss -lntp
```

If `sudo -l` names a Python or shell wrapper, read the permitted file before supplying arguments:

```bash
sudo -n -l
sed -n '1,260p' "$SudoScript"
grep -nE 'docker|inspect|subprocess|full-checkup|arg_list|action' "$SudoScript"
```

For a wrapper that exposes Docker actions, preserve the JSON environment output as private loot:

```bash
boxset DockerFormat '{{json .Config.Env}}'
sudo /usr/bin/python3 "$SudoScript" docker-ps
sudo /usr/bin/python3 "$SudoScript" docker-inspect "$DockerFormat" "$ContainerName" \
  > "$BoxDir/loot/$ContainerName-env.json"
chmod 600 "$BoxDir/loot/$ContainerName-env.json"
```

Repeat the inspection for each named database or application container, using a separate private output file:

```bash
sudo /usr/bin/python3 "$SudoScript" docker-inspect "$DockerFormat" "$DatabaseContainer" \
  > "$BoxDir/loot/$DatabaseContainer-env.json"
chmod 600 "$BoxDir/loot/$DatabaseContainer-env.json"
```

Search only the saved private files for candidate values. Do not print the values into the transcript or a report:

```bash
grep -Ein 'user|username|pass|password|secret|token|database|admin' \
  "$BoxDir/loot/$ContainerName-env.json" \
  "$BoxDir/loot/$DatabaseContainer-env.json"
```

## Why this matters

Containers commonly bind their management ports to loopback, so an external scan can miss an application that is still reachable from the compromised host. Docker environment variables can also carry database and application credentials. The wrapper syntax matters: Docker's Go template is an output format, while the container name is a separate argument.

When a root wrapper passes user-controlled arguments into a Docker action, inspect its parser and subprocess call. A second vulnerability may exist in the wrapper itself, independent of Docker permissions.

## What did you get?

- [ ] The user is in the `docker` group → **Go to [[OSCP/MODULES/18. Linux Privilege Escalation|Linux Privilege Escalation]] and preserve the group evidence**
- [ ] A wrapper can inspect a named container → **Save its environment privately, then route candidates to [[Linux - Credential Search]]**
- [ ] A container exposes a loopback-only application → **Inspect the application locally and return to [[Linux - Web Enum]]**
- [ ] A sudo wrapper calls a relative helper → **Read the exact working-directory behavior and go to [[Linux - Sudo Check]]**
- [ ] Docker is absent or inaccessible → **Return to [[Linux - Local Enum]] and continue SUID, capability, cron, service, and credential checks**

## Gotchas

- `docker inspect` needs both the format expression and the container name when using the standard CLI. A wrapper may reverse or rename these arguments, so read its source.
- A loopback bind is not evidence that the service is irrelevant. Test it from the target shell.
- Keep environment output mode `600`; it may contain database root or application administrator credentials.
- Validate one candidate against the service indicated by the variable names. Do not spray a recovered value across unrelated accounts.

## Seen in

- [[OSCP/BOXES/WRITE UPS/Linux/Busqueda|Busqueda]] -- sudo Python wrapper exposed Docker container names and environment credentials before a Gitea pivot

## Related stages

- [[Linux - Local Enum]]
- [[Linux - Sudo Check]]
- [[Linux - Credential Search]]
- [[Linux - Web Enum]]
- [[Linux - Clean Down]]

## External Resources

- [Docker inspect reference](https://docs.docker.com/reference/cli/docker/inspect/)
- [HackTricks Docker breakout](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/docker-security.html)

## Why this matters for OSCP

This page turns container inspection into a bounded evidence step instead of an assumption that Docker automatically means root.
