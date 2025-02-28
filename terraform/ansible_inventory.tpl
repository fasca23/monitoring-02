---
%{~ for i in databases ~}

${i.name}:
  hosts:
    ${i.name}: 
      ansible_host: ${i["network_interface"][0]["nat_ip_address"]==null ? i["network_interface"][0]["ip_address"] : i["network_interface"][0]["nat_ip_address"]}
      ansible_user: ubuntu
  %{~ endfor ~}