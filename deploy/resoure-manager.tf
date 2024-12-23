resource "yandex_resourcemanager_folder_iam_binding" "roles" {
  folder_id = local.folder_id
  for_each = toset([
    "container-registry.images.puller", "serverless.containers.invoker",
    "serverless-containers.editor", "container-registry.images.pusher", "iam.serviceAccounts.user"
  ])
  members = [
    "serviceAccount:${yandex_iam_service_account.movies_api_sa.id}"
  ]
  role = each.key
}
