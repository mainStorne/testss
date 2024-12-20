resource "yandex_container_registry" "sls" {
  name = "sls"
  folder_id = local.folder_id
}

resource "yandex_container_repository" "api_repository" {
  name = "${yandex_container_registry.sls.id}/api"
}

resource "yandex_serverless_container" "container" {
  image {
    url = "cr.yandex/crp31fj9u7aj7h70jn5t/api:79b7acdbbf599edb3d0585e9af328aaad19757e8"
  }
  service_account_id = yandex_iam_service_account.movies_api_sa.id
  memory = 128
  folder_id = local.folder_id
  name   = "sls-2"
}


resource "yandex_container_repository_lifecycle_policy" "my_lifecycle_policy" {
  name          = "destroy"
  status        = "active"
  repository_id = yandex_container_repository.api_repository.id

  rule {
    description   = "destroy"
    untagged      = false
    tag_regexp    = ".*"
    retained_top  = 1
    expire_period = "24h"
  }
}


output "api_repository_name" {
  value = "cr.yandex/${yandex_container_repository.api_repository.name}"
}

