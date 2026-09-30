variable "project_id" { type = string }
variable "service_account_email" { type = string }

# Grant Cloud Trace Agent to Agent Engine SA
resource "google_project_iam_member" "trace_agent" {
  project = variable.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${variable.service_account_email}"
}

# Grant Cloud Logging Log Writer to Agent Engine SA
resource "google_project_iam_member" "log_writer" {
  project = variable.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${variable.service_account_email}"
}

# Cloud DLP De-identification Template for PII scrubbing
resource "google_data_loss_prevention_deidentify_template" "bakeoff_dlp_template" {
  parent       = "projects/${variable.project_id}/locations/global"
  display_name = "BakeOff PII De-identification Template"
  description  = "Redacts emails, phone numbers, API keys, and auth tokens before logging or egress."

  deidentify_config {
    info_type_transformations {
      transformations {
        primitive_transformation {
          replace_with_info_type_config = true
        }
        info_types { name = "EMAIL_ADDRESS" }
        info_types { name = "PHONE_NUMBER" }
        info_types { name = "AUTH_TOKEN" }
        info_types { name = "API_KEY" }
      }
    }
  }
}

output "dlp_template_name" {
  value = google_data_loss_prevention_deidentify_template.bakeoff_dlp_template.name
}
