variable "customer_project_id" { type = string }
variable "region" { type = string }
variable "service_account_email" { type = string }

resource "google_cloud_run_v2_service" "a2a_runner" {
  project  = variable.customer_project_id
  name     = "bakeoff-runner-a2a"
  location = variable.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = variable.service_account_email
    containers {
      image = "gcr.io/${variable.customer_project_id}/bakeoff-runner-a2a:latest"
      resources {
        limits = {
          cpu    = "2000m"
          memory = "2Gi"
        }
      }
      env {
        name  = "ENVIRONMENT"
        value = "production"
      }
    }
  }
}

output "service_url" {
  value = google_cloud_run_v2_service.a2a_runner.uri
}
