# GCP Terraform Outputs

output "backend_url" {
  description = "Backend Cloud Run service URL"
  value       = google_cloud_run_service.backend.status[0].url
}

output "frontend_url" {
  description = "Frontend Cloud Run service URL"
  value       = google_cloud_run_service.frontend.status[0].url
}

output "database_instance" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.postgres.name
}

output "database_connection" {
  description = "Database connection name"
  value       = google_sql_database_instance.postgres.connection_name
  sensitive   = true
}

output "database_private_ip" {
  description = "Database private IP address"
  value       = google_sql_database_instance.postgres.private_ip_address
  sensitive   = true
}

output "vpc_connector" {
  description = "VPC Access Connector name"
  value       = google_vpc_access_connector.connector.name
}
