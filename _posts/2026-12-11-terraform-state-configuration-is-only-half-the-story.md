---
title: "Terraform State: The Configuration Is Only Half the Story"
slug: terraform-state-configuration-is-only-half-the-story
date: 2026-12-11
categories:
  - DevOps
tags:
  - Terraform
  - infrastructure-as-code
  - state
  - troubleshooting
description: "Use a disposable local-file experiment to separate Terraform configuration, state and actual resources, and understand why Git alone cannot recover the whole deployment."
toc: true
---

The configuration is in Git. You clone the repository on another machine, run Terraform, and expect it to know about everything the first machine created.

There is a missing piece: which existing objects belong to those resource blocks?

In [Read the Plan Before You Apply]({{ '/devops/terraform-plan-before-apply/' | relative_url }}), the question was what Terraform intended to change. Here, let's look at how it knows what it is changing. We can do that with one local file, without asking a cloud account to fund the explanation.

## Three Things That Can Disagree

The configuration describes the resources we want. **State** records the association between Terraform resource addresses and the objects it manages, alongside recorded attributes. The actual resources are what the provider finds when it checks the system.

Those are three related things, not three copies of the same truth. Someone can remove a resource outside Terraform while both the configuration and the last state snapshot still refer to it.

A normal plan refreshes its view of tracked resources through their providers, then compares that information with the configuration. State gives Terraform the associations to work from; it is not a live inventory of everything in an account.

![After note.txt is manually deleted, configuration still asks for it and state still records its resource address. The provider finds the file missing, so a normal Terraform plan proposes creating it again.]({{ '/assets/images/terraform-state/configuration-state-resource.svg' | relative_url }})

## Give Terraform One Disposable File

Use **Bash on Linux or macOS**, Terraform 1.5 or later, and a **new, empty directory**. Save the companion [main.tf]({{ '/assets/code/terraform-state/main.tf' | relative_url }}) there. Initialisation needs network access to download HashiCorp's `local` provider.

The configuration uses the local backend and manages only `note.txt` beside `main.tf`. Its resource block is:

```hcl
resource "local_file" "note" {
    filename        = "${path.module}/note.txt"
    content         = "Managed by Terraform\n"
    file_permission = "0600"
}
```

This is deliberately disposable. The local-file provider can overwrite an existing file at its configured path, which is why we started in an empty directory.

From that directory:

```bash
terraform init
terraform validate
terraform plan
terraform apply
```

Review the proposed creation of `local_file.note`, then enter `yes` at the apply prompt. This creates the file and records the resource in local state. It does not create cloud infrastructure.

Inspect the result:

```bash
cat note.txt
terraform state list
terraform state show local_file.note
```

`state list` should include `local_file.note`: the resource type and the name from our block. `state show` displays the stored attributes for that address. Neither command proves the file still exists; they inspect state.

## Change Reality Without Changing the Configuration

Delete just the file we created:

```bash
rm -- note.txt

terraform state list
terraform plan
```

The address is still in state immediately after the deletion. Terraform did not receive a notification when we removed the file.

During planning, the local provider checks it and discovers that it is missing. With Terraform 1.17.2 and local provider 2.9.1, this lab proposes **one creation, no changes and no destructions**. The configuration still asks for the file, so recreating it is the way back to the declared result.

The plan itself leaves `note.txt` absent. It also does not persist the refreshed state snapshot; this is a proposal, not a repair already performed. Run `terraform apply`, review the new plan and approve that single creation to restore the file.

A missing server can lead to a similar question, but not necessarily such a cheap answer. Recreating its resource does not recover the application data that used to be on it. Our little text file has the considerable advantage of containing nothing important :)

## Why Cloning Git Is Not Enough

By default, this lab stores its snapshot in `terraform.tfstate` in the working directory. That file is separate from `main.tf`. The `.terraform.lock.hcl` file records provider selections; it does not replace resource state.

Lose the state and Terraform loses its recorded associations. That does **not** delete the real objects. A later plan might propose creating resources already present elsewhere, or encounter conflicts, instead of adopting them automatically. Deleting state is therefore not a reset button for a confusing plan.

In a shared project, first check the working directory, selected workspace and backend. Cloning the configuration is useful; connecting to the correct state is another part of the setup. Importing or repairing associations deserves a deliberate procedure, not an improvised edit to the JSON.

This is also why state belongs in protected storage rather than Git. It can contain sensitive values, even when terminal output hides them. A shared backend can provide controlled access and, where supported, locking to coordinate state writes. Locking does not stop someone changing infrastructure through a console, and it does not replace backups.

## Finish the Experiment

In this lab directory only:

```bash
terraform destroy
```

Review and approve removal of the one managed file. Terraform leaves the configuration, provider files and state artifacts in the directory; destroying resources does not remove the whole workspace.

The useful habit is to keep the three questions separate: what does the configuration request, what associations does state record, and what does the provider find now? A surprising plan becomes easier to investigate once we stop treating those as the same answer.

### Further Reading

- [Why Terraform needs state](https://developer.hashicorp.com/terraform/language/state/purpose)
- [Planning and refresh behaviour](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [The local-file provider's behaviour](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file)
- [Sensitive values in Terraform](https://developer.hashicorp.com/terraform/language/manage-sensitive-data)
- [Remote state storage](https://developer.hashicorp.com/terraform/language/state/remote) and [locking](https://developer.hashicorp.com/terraform/language/state/locking)
