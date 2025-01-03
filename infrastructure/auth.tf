resource "yandex_serverless_container" "authorizer" {
  name               = "authorizer"
  service_account_id = yandex_iam_service_account.movies_api_sa.id
  memory             = 128
  folder_id          = local.folder_id
  image {
    url = "cr.yandex/crp31fj9u7aj7h70jn5t/auth:latest"
    environment = {
      IS_DEBUG = "False"
      DOCUMENT_API_ENDPOINT = yandex_ydb_database_serverless.ydb.ydb_api_endpoint
      DOCUMENT_DATABASE_PATH  = yandex_ydb_database_serverless.ydb.database_path
    }
  }
}