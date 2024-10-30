packer {
  required_plugins {
    googlecompute = {
      source  = "github.com/hashicorp/googlecompute"
      version = "~> 1"
    }
  }
}


variable "project_id" {
  default = "YOUR_PROJECT_ID"
  type        = string
}

variable "source_image_family" {
  default = "centos-stream-8"
  type        = string
}

variable "ssh_username" {
  default = "YOUR_SSH_USERNAME"
  type        = string
}

variable "zone" {
  default = "us-east1-b"
  type        = string
}





source "googlecompute" "example" {
  project_id = var.project_id
  source_image_family = var.source_image_family
  ssh_username = var.ssh_username
  image_name = "my-custom-image-${formatdate("YYYYMMDDHHmmss", timestamp())}"
  image_family        = "custom-centos"
  zone = var.zone
  machine_type        = "e2-medium"
  disk_size           = 30
  disk_type           = "pd-standard"
  subnetwork          = "default"
} 
build {
  sources = [
    "source.googlecompute.example"
  ]
  provisioner "shell" {
    script = "scripts/user_installations.sh"
  }

  provisioner "file" {
    source      = "./webapp-main.zip"
    destination = "/tmp/webapp-main.zip"
  }


  provisioner "file" {
    source      = "./webapp.service"
    destination = "/tmp/webapp.service"
  }

    provisioner "file" {
    source      = "./appconfig.yaml"
    destination = "/tmp/appconfig.yaml"
  }


  provisioner "shell" {
    script = "scripts/filehandling.sh"
  }

  provisioner "shell" {
    script = "scripts/requirements.sh"
    execute_command = "sudo {{ .Path }}"
  }

  // File handling and permissions
  provisioner "shell" {
    script = "scripts/webapp_setup.sh"
  }


}
