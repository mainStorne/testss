resource "yandex_api_gateway" "api_gateway" {
  name = "apigateway"
  spec = templatefile("./openapi/api.yml", {
      API_SA_ID = yandex_iam_service_account.movies_api_sa.id
      CONTAINER_ID = yandex_serverless_container.container.id
  })
}