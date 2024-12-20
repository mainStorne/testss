resource "yandex_container_registry" "sls" {
  name = "sls"
  folder_id = local.folder_id
}

resource "yandex_container_repository" "api_repository" {
  name = "${yandex_container_registry.sls.id}/api"
}


resource "yandex_serverless_container" "container" {
  image {
    url = "cr.yandex/crp31fj9u7aj7h70jn5t/api:9a2037d1d9c687e5dfc3f82ed34b1f992b153458"
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

resource "null_resource" "build_and_push_authorizer_image" {


  provisioner "local-exec" {
    command = <<EOT
      cd ../services/auth
      docker build -t cr.yandex/${yandex_container_registry.sls.id}/auth:latest .
      yc container registry configure-docker
      docker push cr.yandex/${yandex_container_registry.sls.id}/auth:latest
    EOT
  }

}

resource "yandex_serverless_container" "authorizer" {
  name   = "authorizer"
  service_account_id = yandex_iam_service_account.movies_api_sa.id
  memory = 128
  folder_id = local.folder_id
  image {
    url = "cr.yandex/${yandex_container_registry.sls.id}/auth:latest"
  }
  depends_on = [null_resource.build_and_push_authorizer_image]
}


output "api_repository_name" {
  value = "cr.yandex/${yandex_container_repository.api_repository.name}"
}


