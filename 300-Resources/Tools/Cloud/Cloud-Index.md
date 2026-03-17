---
tags: [index, cloud, moc]
---

# Cloud Penetration Testing Tools Index

## Quick Navigation

| Category | Tools |
|----------|-------|
| Multi-Cloud | prowler, scoutsuite, cloudsploit |
| AWS | aws-cli, pacu, enumerate-iam, s3scanner, aws-recon, aws-nuke, cloudmapper, pmapper, dufflebag |
| Azure | azure-cli, microburst, stormspotter, azurehound, azucar, powerzure |
| GCP | gcloud, gcpwn, gcpbucketbrute, gcp-iam-collector |
| Kubernetes | kube-hunter, kube-bench, kubescape, kube-score, kube-linter, kubeaudit, popeye, k9s, peirates, boop, kubesploit, polaris |
| Container | trivy |
| IaC | checkov, tfsec, terrascan, kics |

---

## Multi-Cloud Security

- [[prowler]] - AWS security assessment tool
- [[scoutsuite]] - Multi-cloud security auditing
- [[cloudsploit]] - Cloud security scanning
- [[trivy]] - Container and cloud vulnerability scanner

## AWS Tools

- [[aws-cli]] - Official AWS command line interface
- [[pacu]] - AWS exploitation framework
- [[enumerate-iam]] - IAM permission enumeration
- [[s3scanner]] - Find open S3 buckets
- [[aws-recon]] - AWS resource enumeration
- [[aws-nuke]] - Delete all AWS resources
- [[cloudmapper]] - AWS visualization and analysis
- [[pmapper]] - IAM privilege escalation analysis
- [[dufflebag]] - Search EBS snapshots for secrets

## Azure Tools

- [[azure-cli]] - Official Azure command line interface
- [[microburst]] - Azure enumeration framework
- [[stormspotter]] - Azure visualization
- [[azurehound]] - BloodHound for Azure AD
- [[azucar]] - Azure security assessment
- [[powerzure]] - PowerShell Azure toolkit

## GCP Tools

- [[gcloud]] - Official Google Cloud CLI
- [[gcpwn]] - GCP exploitation framework
- [[gcpbucketbrute]] - Google storage bucket enumeration
- [[gcp-iam-collector]] - IAM permission collector

## Kubernetes Security

- [[kube-hunter]] - Kubernetes penetration testing
- [[kube-bench]] - CIS benchmark checks
- [[kubescape]] - Comprehensive security scanning
- [[kube-score]] - Object analysis and scoring
- [[kube-linter]] - YAML linting and validation
- [[kubeaudit]] - Security auditing
- [[popeye]] - Cluster sanitizer
- [[k9s]] - Terminal UI for K8s
- [[peirates]] - K8s penetration testing
- [[boop]] - Security toolkit
- [[kubesploit]] - Post-exploitation framework
- [[polaris]] - Configuration validator

## Infrastructure as Code (IaC)

- [[checkov]] - Static analysis for IaC
- [[tfsec]] - Terraform security scanner
- [[terrascan]] - IaC security scanner
- [[kics]] - Keeping Infrastructure as Code Secure

---

## Quick Reference by Phase

### Phase 1: Cloud Reconnaissance

# AWS
aws s3 ls
aws ec2 describe-instances
enumerate-iam --access-key KEY --secret-key SECRET

# Azure
az login
az vm list
azurehound -u user@domain.com -p pass list

# GCP
gcloud auth login
gcloud compute instances list
gcpbucketbrute -k keyword

# Kubernetes
kubectl get pods --all-namespaces
kube-hunter --local
kube-bench

### Phase 2: Security Assessment

prowler
scout aws
trivy image nginx:latest
checkov -d .
tfsec .

### Phase 3: Exploitation

pacu
gcpwn
peirates

### Phase 4: Cleanup

aws-nuke -c config.yml --dry-run
