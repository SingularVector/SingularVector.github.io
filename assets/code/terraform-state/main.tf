terraform {
    required_version = ">= 1.5.0"

    required_providers {
        local = {
            source  = "hashicorp/local"
            version = "~> 2.6"
        }
    }
}

# Only this disposable file is managed; no cloud account is involved.
resource "local_file" "note" {
    filename        = "${path.module}/note.txt"
    content         = "Managed by Terraform\n"
    file_permission = "0600"
}
