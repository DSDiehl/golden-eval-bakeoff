variable "project_id" { type = string }
variable "region" { type = string }

resource "google_bigquery_dataset" "eval_warehouse" {
  project     = variable.project_id
  dataset_id  = "model_bakeoff_telemetry"
  location    = variable.region
  description = "Analytical warehouse for model bake-off evaluations, token telemetry, and TCO facts."
}

resource "google_bigquery_table" "eval_results" {
  project    = variable.project_id
  dataset_id = google_bigquery_dataset.eval_warehouse.dataset_id
  table_id   = "eval_results"

  time_partitioning {
    type = "DAY"
  }

  schema = jsonencode([
    { name = "run_id", type = "STRING", mode = "REQUIRED" },
    { name = "account_id", type = "STRING", mode = "REQUIRED" },
    { name = "case_id", type = "STRING", mode = "REQUIRED" },
    { name = "candidate_model", type = "STRING", mode = "REQUIRED" },
    { name = "overall_score", type = "FLOAT", mode = "REQUIRED" },
    { name = "verdict", type = "STRING", mode = "REQUIRED" },
    { name = "latency_ms", type = "FLOAT", mode = "REQUIRED" },
    { name = "input_tokens", type = "INTEGER", mode = "REQUIRED" },
    { name = "output_tokens", type = "INTEGER", mode = "REQUIRED" },
    { name = "timestamp", type = "TIMESTAMP", mode = "REQUIRED" }
  ])
}

output "dataset_id" {
  value = google_bigquery_dataset.eval_warehouse.dataset_id
}
