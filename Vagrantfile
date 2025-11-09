# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  #===============================#
  # Ansible Server for NXOSv TEST #
  #===============================#
  
  config.vm.define "ansible-server" do |cfg|
    cfg.vm.box = "generic/ubuntu1804"
	cfg.vm.box_version = "4.3.12"
	cfg.vm.host_name = "ansible-server"
	cfg.vm.network "public_network", ip: "192.168.45.55"
	cfg.vm.network "forwarded_port", guest: 22, host: 19255, auto_correct: true, id: "ssh"
	cfg.vm.synced_folder "../data", "/vagrant", disabled: true
	cfg.vm.provision "shell", inline: "apt-get update -y"   
	cfg.vm.provision "shell", inline: "apt-get install ansible -y"
	cfg.vm.provision "file", source: "ansible_env_ready.yml", destination: "ansible_env_ready.yml"
	cfg.vm.provision "shell", inline: "ansible-playbook ansible_env_ready.yml"
	cfg.vm.provider "virtualbox" do |vb|
	  vb.name = "Ansible-Server(NXOSv)"
	end
  end
end