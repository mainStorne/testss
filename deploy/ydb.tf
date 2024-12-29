locals {
  db_name = "db"
}

resource "yandex_ydb_database_serverless" "ydb" {
  name = local.db_name
  folder_id = local.folder_id
}


output "api_endpoint" {
  value = yandex_ydb_database_serverless.ydb.ydb_api_endpoint
}

output "database_path" {
  value = yandex_ydb_database_serverless.ydb.database_path
}