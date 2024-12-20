
data "archive_file" "authorizer-src" {
  output_path = "../dist/authorizer-src.zip"
  type = "zip"
  source {
    content  = file("../authorizer/authorize.py")
    filename = "authorize.py"
  }
}

resource "yandex_function" "authorizer" {
  entrypoint = "authorize.handler"
  memory     = 128
  name       = "authorizer"
  folder_id = local.folder_id
  user_hash = data.archive_file.authorizer-src.output_base64sha256
  runtime    = "python312"
  service_account_id = yandex_iam_service_account.movies_api_sa.id
  content {
    zip_filename = data.archive_file.authorizer-src.output_path
  }
}