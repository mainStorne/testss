resource "yandex_container_registry" "sls" {
  name = "sls"
  folder_id = local.folder_id
}

resource "yandex_container_repository" "api_repository" {
  name = "${yandex_container_registry.sls.id}/api"
}



output "api_repository_name" {
  value = "cr.yandex/${yandex_container_repository.api_repository.name}"
}

