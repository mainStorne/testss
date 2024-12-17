resource "yandex_resourcemanager_folder_iam_binding" "docker-pull" {
  folder_id = local.folder_id
  members = [
    "serviceAccount:${yandex_iam_service_account.movies_api_sa.id}"
  ]
  role      = "container-registry.images.puller"
}

resource "yandex_resourcemanager_folder_iam_binding" "docker-invoker" {
  folder_id = local.folder_id
  members = [
    "serviceAccount:${yandex_iam_service_account.movies_api_sa.id}"
  ]
  role      = "serverless.containers.invoker"
}


resource "yandex_resourcemanager_folder_iam_binding" "sls-editor" {
  folder_id = local.folder_id
  members = [
    "serviceAccount:${yandex_iam_service_account.movies_api_sa.id}"
  ]
  role      = "serverless-containers.editor"
}
