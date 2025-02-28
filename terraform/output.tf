

### По заданию 7

output "vpc_info" {
  value = { for key, value in local.vpc :
    key => can(tolist(value)) ? [for i in value : i if index(value, i) != 2] : value
  }
}