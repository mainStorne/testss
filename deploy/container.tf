
resource "yandex_serverless_container" "container" {
  image {
    url = "cr.yandex/crp31fj9u7aj7h70jn5t/api:49791dab738884dfbba78506aa6aaafac2b329ec"
  }
  service_account_id = yandex_iam_service_account.movies_api_sa.id
  memory = 128
  folder_id = local.folder_id
  name   = "sls-2"
}
