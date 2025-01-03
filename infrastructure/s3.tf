locals {
  user_profiles_bucket_prefix = "user-profiles"
  frontend_bucket_prefix      = "frontend"
}

resource "yandex_storage_bucket" "user_profiles_bucket" {
  bucket     = "${local.user_profiles_bucket_prefix}-${local.folder_id}"
  access_key = yandex_iam_service_account_static_access_key.static-key.access_key
  secret_key = yandex_iam_service_account_static_access_key.static-key.secret_key
}

resource "yandex_storage_bucket" "frontend_bucket" {
  bucket     = "${local.frontend_bucket_prefix}-${local.folder_id}"
  access_key = yandex_iam_service_account_static_access_key.static-key.access_key
  secret_key = yandex_iam_service_account_static_access_key.static-key.secret_key
}

output "user_profiles_bucket" {
  value = yandex_storage_bucket.user_profiles_bucket.bucket
}

output "frontend_bucket" {
  value = yandex_storage_bucket.frontend_bucket.bucket
}