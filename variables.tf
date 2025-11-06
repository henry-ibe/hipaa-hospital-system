variable "hospital_name" {
  description = "Hospital name"
  type        = string
}

variable "location" {
  description = "Hospital location"
  type        = string
}

variable "allowed_ip_ranges" {
  description = "IP ranges allowed to access"
  type        = list(string)
}

variable "allowed_states" {
  description = "US states allowed"
  type        = list(string)
}
