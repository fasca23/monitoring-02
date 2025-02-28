
### По заданию 4

# Исправление ошибки №2

resource "local_file" "ansible_inventory" {
  content = templatefile("${path.module}/ansible_inventory.tpl",
   {databases = yandex_compute_instance.db
    }
  )
  filename = "${abspath(path.module)}/playbook/inventory/hosts.yml"
}
