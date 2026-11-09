terraform {
  required_providers {
    multipass = {
      source  = "larstobi/multipass"
      version = "1.4.2"
    }
  }
}

provider "multipass" {}

resource "multipass_instance" "statusboard_vm" {
  name   = "statusboard-tf"
  image  = "24.04"
  cpus   = 2
  memory = "2G"
  disk   = "10G"
}

