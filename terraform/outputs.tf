output "agent_engine_id" {
  description = "Resource ID of the deployed Vertex AI Agent Engine coordinator instance."
  value       = module.agent_engine.agent_engine_id
}

output "a2a_cloud_run_url" {
  description = "The HTTPS invocation endpoint for the customer-side A2A runner."
  value       = module.cloudrun_a2a.service_url
}

output "bigquery_dataset_id" {
  description = "BigQuery dataset storing bakeoff evaluations, telemetry, and TCO facts."
  value       = module.bigquery.dataset_id
}

output "secrets_managed" {
  description = "List of Secret Manager resource IDs provisioned for multi-vendor access."
  value       = module.secrets.secret_ids
}
