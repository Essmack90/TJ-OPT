Let's build this as one full story, from "what even is a pod" all the way to "here's the leaked AWS key." I'll use one diagram you can follow top to bottom, plain-English explanations under each part, and a single copy-paste command block at the end.## The story, one step at a time
![[Pasted image 20260713152714.png]]

**Step 1 — Your laptop** You're on Kali. Kubernetes is running somewhere else — inside minikube, which is basically a tiny pretend cluster living on your machine, but it's _sealed off_ from you like a fish tank. You can look at it with `kubectl`, but you can't just walk up and touch anything inside it. That's on purpose — it's how real clusters work too, for security.

**Step 2 — kubectl port-forward** Since the fish tank is sealed, you need a straw poked through the glass. That's what `port-forward` does: it opens a tunnel from a port on your laptop (`localhost:3000`) straight through to something inside the cluster. Important quirk: this command doesn't "finish" — it just sits there holding the tunnel open forever, printing a log line every time something uses it. That's why it looked "stuck." It wasn't broken, it was working exactly as intended. You just need a **second terminal window** to actually use the tunnel while the first one holds it open.

**Step 3 — Service** Inside the cluster, apps don't get a fixed address — pods get recreated all the time and get a new IP each time. So Kubernetes gives you a **Service**, which is like a reception desk with a phone number that never changes. You call the Service, and it forwards you to whichever pod is currently running. `build-code-service` is that reception desk for this app.

**Step 4 — Pod** The Service hands you off to the **Pod** — this is the actual running copy of the app, a container doing real work. In this case it's a small web server (`madhuakula/k8s-goat-build-code`) listening on port 3000.

**Step 5 — .git exposed** Here's where it stops being about Kubernetes and becomes an app bug. This web server was set up wrong: instead of only serving its finished, built website, it's serving its **entire project folder**, including a hidden folder called `.git`. That folder is the app's full diary — every change ever made to the code, forever, including stuff that was later deleted. Nobody was supposed to be able to see it from outside, but because of the misconfiguration, anyone who knows to ask for `/.git/HEAD` gets an answer.

**Step 6 — git-dumper** Once you know `.git` is reachable, a tool called `git-dumper` will fetch every single file inside it, piece by piece, and rebuild the whole project — including its full diary — on your own machine. Think of it like recovering someone's entire diary by photographing every page through a crack in a door, one page at a time, then stapling it all back together at home.

**Step 7 — Secrets found** Now that you have the diary, you don't just read today's page — you read **every page ever written**. Someone had typed an AWS username and password into the code at some point, then later "deleted" it in a newer entry. But deleting a page from a diary doesn't erase the fact that it was written on an earlier page — the old page is still there if you flip back far enough. That's exactly what `git log -p --all` does: it flips through every page (every commit) instead of just the most recent one, and that's how the AWS key turns up even though it's not in the current version of the code.

---

## Full copy-paste command sequence

```bash
# 1. Start the cluster and deploy Kubernetes Goat (if not already running)
minikube start
cd ~/kubernetes-goat/kubernetes-goat
bash setup-kubernetes-goat.sh

# 2. Recon: see what's running and find the target
kubectl get pods
kubectl describe pod <build-code-pod-name>
kubectl get svc | grep build-code

# 3. Open the tunnel (leave this running — it does NOT return control of the terminal)
kubectl port-forward svc/build-code-service 3000:3000

# ---------------------------------------------
# Open a SECOND terminal for everything below
# ---------------------------------------------

# 4. Check whether .git is exposed
curl http://localhost:3000/.git/HEAD
# expect: ref: refs/heads/master  <-- if you see this, it's exposed

# 5. Install the dumping tool (one-time only)
pip install git-dumper --break-system-packages

# 6. Pull down the whole repo, including its full history
git-dumper http://localhost:3000/.git/ ./build-code-dump

# 7. See every commit ever made
cd build-code-dump
git log --all --oneline

# 8. Search EVERY commit's changes (not just the latest code) for leaked secrets
git log --all -p | grep -iE "key|secret|password|token|aws"

# When you're done, go back to the first terminal and Ctrl+C to close the tunnel
```

Quick sanity check for next time you try this on a new target: if step 4 gives you a `200` with a `ref:` line instead of a `404`, you've got a live one — go straight to `git-dumper`.