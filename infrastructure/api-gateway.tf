resource "yandex_api_gateway" "api_gateway" {
  name = "apigateway"
  spec = templatefile("./openapi/api.yml", {
    API_SA_ID         = yandex_iam_service_account.movies_api_sa.id
    API_CONTAINER_ID  = yandex_serverless_container.container.id
    AUTH_CONTAINER_ID = yandex_serverless_container.authorizer.id
  })
}

resource "yandex_api_gateway" "frontend_gateway" {
  name = "frontend-gateway"
  spec = templatefile("./openapi/frontend.yml", {
    BUCKET_NAME = yandex_storage_bucket.frontend_bucket.bucket
    API_SA_ID   = yandex_iam_service_account.movies_api_sa.id
  })
}