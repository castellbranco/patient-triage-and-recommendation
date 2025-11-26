# GCP Terraform Variables

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "patient-triage"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (development, staging, production)"
  type        = string
  default     = "development"
}

# Database variables
variable "database_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "triage_db"
}

variable "database_user" {
  description = "PostgreSQL database user"
  type        = string
  default     = "triage_user"
}

variable "database_password" {
  description = "PostgreSQL database password"
  type        = string
  sensitive   = true
}

variable "db_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-f1-micro" # Smallest tier for development
}

# Application variables
variable "backend_image" {
  description = "Backend Docker image"
  type        = string
}

variable "frontend_image" {
  description = "Frontend Docker image"
  type        = string
}

variable "secret_key" {
  description = "JWT secret key"
  type        = string
  sensitive   = true
}

# Scaling variables
variable "min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 0 # Scale to zero for cost savings
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

# Resource limits
variable "backend_cpu" {
  description = "Backend CPU limit"
  type        = string
  default     = "1000m" # 1 vCPU
}

variable "backend_memory" {
  description = "Backend memory limit"
  type        = string
  default     = "512Mi"
}

variable "frontend_cpu" {
  description = "Frontend CPU limit"
  type        = string
  default     = "1000m"
}

variable "frontend_memory" {
  description = "Frontend memory limit"
  type        = string
  default     = "256Mi"
}

# Security
variable "allow_public_access" {
  description = "Allow public access to Cloud Run services"
  type        = bool
  default     = true # Set to false for production with IAP/Load Balancer
}
