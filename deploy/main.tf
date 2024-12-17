
provider "yandex" {
  token     = var.token
  cloud_id  = local.cloud_id
  folder_id = local.folder_id
  zone      = local.zone
}

locals {
  zone = "ru-central1-a"
  cloud_id  = var.cloud_id
  folder_id = var.folder_id
  service_account_name_prefix = "api-sa"
}
