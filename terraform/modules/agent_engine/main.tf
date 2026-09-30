variable "project_id" { type = string }
variable "region" { type = string }
variable "environment" { type = string }

resource "google_service_account" "agent_engine_sa" {
  project      = variable.project_id
  account_id   = "bakeoff-coordinator-sa"
  display_name = "Bake-Off Coordinator Agent Engine Service Account"
}

# IAM role for Vertex AI execution
resource "google_project_iam_member" "vertex_user" {
  project = variable.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agent_engine_sa.email}"
}

output "agent_engine_id" {
  value = "projects/${variable.project_id}/locations/${variable.region}/agents/bakeoff-coordinator-${variable.environment}"
}

output "service_account_email" {
  value = google_service_account.agent_engine_sa.email
}
