terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.30.0"
    }
  }
}

provider "google" {
  project = variable.project_id
  region  = variable.region
}

# Module 1: Vertex AI Agent Engine Coordinator Runtime
module "agent_engine" {
  source      = "./modules/agent_engine"
  project_id  = variable.project_id
  region      = variable.region
  environment = variable.environment
}

# Module 2: BigQuery Telemetry & Analytical Warehouse
module "bigquery" {
  source     = "./modules/bigquery"
  project_id = variable.project_id
  region     = variable.region
}

# Module 3: Multi-Vendor Secret Manager & WIF bindings
module "secrets" {
  source                = "./modules/secrets"
  project_id            = variable.project_id
  service_account_email = module.agent_engine.service_account_email
}

# Module 4: Cloud Trace, Cloud Logging, and Cloud DLP Templates
module "observability" {
  source                = "./modules/observability"
  project_id            = variable.project_id
  service_account_email = module.agent_engine.service_account_email
}

# Module 5: Customer-Side Cloud Run A2A Runner
module "cloudrun_a2a" {
  source                = "./modules/cloudrun_a2a"
  customer_project_id   = variable.customer_project_id
  region                = variable.region
  service_account_email = module.agent_engine.service_account_email
}
