resource "yandex_container_registry" "sls" {
  name = "sls"
  folder_id = local.folder_id
}

resource "yandex_container_repository" "api_repository" {
  name = "${yandex_container_registry.sls.id}/api"
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



resource "yandex_container_repository" "auth-repo" {
  name = "${yandex_container_registry.sls.id}/auth"
}

resource "yandex_container_repository_lifecycle_policy" "authorizer" {
  repository_id = yandex_container_repository.auth-repo.id
  status        = "active"
    name          = "destroy"
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


