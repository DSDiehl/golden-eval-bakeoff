variable "project_id" { type = string }
variable "service_account_email" { type = string }

# Multi-vendor secrets managed securely
locals {
  secrets = [
    "anthropic-vertex-api-key",
    "a2a-client-bearer-token",
    "bakeoff-signing-hmac-key"
  ]
}

resource "google_secret_manager_secret" "vendor_secrets" {
  for_each  = toset(locals.secrets)
  project   = variable.project_id
  secret_id = each.key

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_iam_member" "secret_accessor" {
  for_each  = toset(locals.secrets)
  project   = variable.project_id
  secret_id = google_secret_manager_secret.vendor_secrets[each.key].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${variable.service_account_email}"
}

output "secret_ids" {
  value = [for s in google_secret_manager_secret.vendor_secrets : s.secret_id]
}
