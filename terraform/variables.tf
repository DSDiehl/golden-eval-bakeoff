variable "project_id" {
  description = "The Google Cloud Project ID where the coordinator and Agent Engine reside."
  type        = string
  default     = "google-eval-bakeoff-prod"
}

variable "region" {
  description = "The default GCP region for Vertex AI and Cloud Run resources."
  type        = string
  default     = "us-central1"
}

variable "customer_project_id" {
  description = "Customer Google Cloud Project ID for the remote A2A runner deployment."
  type        = string
  default     = "customer-isolated-eval-env"
}

variable "environment" {
  description = "Deployment environment name (dev, staging, prod)."
  type        = string
  default     = "prod"
}
