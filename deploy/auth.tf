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
  name               = "authorizer"
  service_account_id = yandex_iam_service_account.movies_api_sa.id
  memory             = 128
  folder_id          = local.folder_id
  image {
    url = "cr.yandex/crp31fj9u7aj7h70jn5t/auth:11031c54e9db0c977c658488c44e4fb69818af39"
    environment = {
      DOCUMENT_API_ENDPOINT = yandex_ydb_database_serverless.ydb.document_api_endpoint
      DOCUMENT_DATABASE_PATH  = yandex_ydb_database_serverless.ydb.database_path
    }
  }
  depends_on = [null_resource.build_and_push_authorizer_image]
}