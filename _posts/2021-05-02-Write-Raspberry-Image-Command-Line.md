---
title: "Write RaspBerry image to SD card via command line"
excerpt: "In this post we will explore how to use bash to write an OS image to an SD card for use with RaspBerryPI"
categories:
  - Linux
  - Azure

tags:
  - Linux
  - Lab

toc: false
header:
    teaser: "/assets/images/shared/Kubernetes_Logo.png"
last_modified_at: 2026-11-02
---

When I originally wrote this, I was in the process of rebuilding my *Docker/Kubernetes* portable cluster which I built using a couple of RaspberryPi 4 and as part of this I needed to *reflash* the various SD cards where operating system for each node is installed.

Usually [Balena Etcher](https://www.balena.io/etcher/) is my go-to tool for such endeavours but being in a rush and not easy way to download the tool on my Linux box I simply used the good old command line, here is how this is done.


## Choose an image and identify the card

These commands target **Linux with GNU tools**. Download a currently supported image for your Raspberry Pi model from the OS publisher and verify its published checksum before writing. The Ubuntu 21.04 filename in the original example is historical, not a current image recommendation.

For a guided workflow, [Raspberry Pi Imager](https://www.raspberrypi.com/documentation/computers/getting-started.html) provides device, OS and storage selection. For a manual write, compare the disk list before and after inserting the card:

```bash
lsblk -o NAME,SIZE,MODEL,TYPE,MOUNTPOINTS
```

Identify the **whole device**, such as `/dev/sdd`, by size and model. A partition such as `/dev/sdd1` is not the write target. Device names can change, so do not reuse a name from this article without checking it.

Writing an image overwrites the selected device. Unmount each mounted partition shown for the card before proceeding; for example, run `sudo umount /dev/sdd1` only if that is an actual mounted partition on the card you identified. Recheck the device list afterward.

## Write the image

In Bash, replace both paths below with the verified image and device:

```bash
set -o pipefail
xzcat ./your-supported-image.img.xz | sudo dd of=/dev/sdd bs=4M conv=fsync status=progress
```

`pipefail` makes a decompression failure fail the pipeline too. `conv=fsync` flushes the output before `dd` completes. Wait for the command to finish successfully before removing the card; if either command fails, do not treat the card as ready to boot.

This assumes an `.img.xz` file. For an uncompressed `.img`, use `sudo dd if=./your-supported-image.img of=/dev/sdd bs=4M conv=fsync status=progress` instead. These GNU command options and `/dev/sd…` names are not macOS instructions.
