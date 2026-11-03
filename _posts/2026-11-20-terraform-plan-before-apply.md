---
title: "Terraform: Read the Plan Before You Apply"
date: 2026-11-20
categories:
  - DevOps
tags:
  - Terraform
  - infrastructure-as-code
description: "Review Terraform changes by separating updates, replacements and deletions, then apply the saved plan you actually inspected."
toc: true
---

Changing one line of infrastructure code can replace an entire server. The size of the Git diff tells you very little about the size of the operation.

An AMI change is a useful example: the configuration looks almost identical, but an existing EC2 instance cannot simply become a machine launched from another image. Before applying, the useful question is: **what will happen to the running resources and their data?**

## Start with the right working directory

For an existing configuration, check the repository, selected workspace and backend before planning. A perfectly valid plan against the wrong environment is still the wrong change.

```bash
terraform init
terraform workspace show
terraform fmt -check
terraform validate
terraform plan -out=review.tfplan
```

`init` prepares the working directory and backend; it does not deploy or destroy infrastructure. `validate` checks the configuration, but it does not prove that a change is operationally safe.

The saved plan captures the proposed operations for review. Treat it as sensitive: plan files can contain values that Terraform hides in terminal output. Keep them out of Git and public build artifacts. See the [plan command reference](https://developer.hashicorp.com/terraform/cli/commands/plan).

## Read the actions, then the reason

The summary is a starting point. Inspect each affected resource, especially anything marked for deletion or replacement.

| Marker | Meaning | Question to answer |
| --- | --- | --- |
| `+` | Create | Is the new resource configured for the intended environment? |
| `~` | Update in place | Can the update interrupt the service? |
| `-` | Delete | Is the resource intentionally being retired? |
| `-/+` | Destroy, then create replacement | What disappears before its replacement exists? |
| `+/-` | Create replacement, then destroy | Can both resources coexist, and how does traffic move? |

For a replacement, look for the attribute annotated `forces replacement`. Then follow dependencies: an instance replacement can also affect addresses, attachments and the application using it. A value marked `known after apply` is not yet available for review; account for that uncertainty rather than treating it as a verified result.

## Lifecycle rules have boundaries

`create_before_destroy` changes replacement ordering. It does not, by itself, provide health checks, traffic switching or application availability. Unique names and capacity limits can also prevent old and new resources from existing together.

`prevent_destroy` rejects plans that would destroy a protected resource while the rule remains in its configuration. Removing the whole resource block also removes that protection. Commenting out a resource and running `apply` is therefore not a harmless way to stop managing it.

Terraform's [lifecycle reference](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle) explains those limits. A lifecycle setting is a constraint on a plan, not a backup or a recovery procedure.

## Apply the reviewed plan

After review, apply the saved file:

```bash
terraform apply review.tfplan
```

This executes the saved plan without another interactive approval prompt. Run it only after approval; do not use it as a preview. A plain `terraform apply` instead generates a fresh plan, which might differ from the one you inspected. See the [apply command reference](https://developer.hashicorp.com/terraform/cli/commands/apply).

If configuration, state or circumstances have changed, generate and review a new plan. Finally, check the service itself: Terraform completing its operations does not establish that the application works.

Before confirming a replacement, you should be able to name the affected resource, explain the replacement trigger and describe what preserves its data. If any of those answers is missing, the plan still needs work.
