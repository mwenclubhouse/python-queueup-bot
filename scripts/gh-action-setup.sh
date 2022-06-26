#!/usr/bin/env bash

""
Instructions:
Setting up WIF: https://cloud.google.com/blog/products/identity-security/enabling-keyless-authentication-from-github-actions
Setting up SSH Keys: https://cloud.google.com/compute/docs/instances/managing-instance-access#gcloud
""

gcloud compute instances add-metadata mwenclubhouse \
    --metadata enable-oslogin=TRUE

gcloud iam workload-identity-pools create "gh-to-vm-pool" \
  --project="mwenclubhouse" \
  --location="global" \
  --display-name="GH Actions to VM Pool"

gcloud iam workload-identity-pools providers create-oidc "gh-to-vm-provider" \
  --project="mwenclubhouse" \
  --location="global" \
  --workload-identity-pool="gh-to-vm-pool" \
  --display-name="GH Actions to VM Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository"\
  --issuer-uri="https://token.actions.githubusercontent.com"

gcloud iam service-accounts add-iam-policy-binding "gh-actions-to-vm@mwenclubhouse.iam.gserviceaccount.com" \
  --project="mwenclubhouse" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/284911242659/locations/global/workloadIdentityPools/gh-to-vm-pool/attribute.repository/mwenclubhouse/python-queueup-bot"

