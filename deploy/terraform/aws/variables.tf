# AWS Terraform Variables

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "patient-triage"
}

variable "environment" {
  description = "Environment (development, staging, production)"
  type        = string
  default     = "development"
}

# Network variables
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
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

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro" # Smallest for development
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

# Application variables
variable "backend_image" {
  description = "Backend Docker image"
  type        = string
  default     = ""
}

variable "frontend_image" {
  description = "Frontend Docker image"
  type        = string
  default     = ""
}

variable "secret_key" {
  description = "JWT secret key"
  type        = string
  sensitive   = true
  default     = ""
}

# ECS variables
variable "backend_cpu" {
  description = "Backend container CPU units"
  type        = number
  default     = 256
}

variable "backend_memory" {
  description = "Backend container memory in MB"
  type        = number
  default     = 512
}

variable "frontend_cpu" {
  description = "Frontend container CPU units"
  type        = number
  default     = 256
}

variable "frontend_memory" {
  description = "Frontend container memory in MB"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 1
}
