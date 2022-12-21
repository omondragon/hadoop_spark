# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|

    if Vagrant.has_plugin? "vagrant-vbguest"
        config.vbguest.no_install  = true
        config.vbguest.auto_update = false
        config.vbguest.no_remote   = true
    end

    config.vm.define "node1" do |node1|
        node1.vm.boot_timeout   = 9000
        node1.vm.box = "bento/ubuntu-22.04"
        node1.vm.provider "virtualbox" do |v|
           v.customize [
                        "modifyvm", :id,
                        "--memory", "1024",
                        "--cpus", "2"]
        end
        node1.vm.network :private_network, ip: "192.168.200.4"
        node1.vm.hostname = "node1"
        node1.vm.provision :shell, path: "scripts/setup-hosts.sh"
        node1.vm.provision :shell, path: "scripts/setup-node.sh"
        node1.vm.provision :shell, path: "scripts/installNode.sh"
    end

    config.vm.define "node2" do |node2|
        node2.vm.boot_timeout   = 9000
        node2.vm.box = "bento/ubuntu-22.04"
        node2.vm.provider "virtualbox" do |v|
           v.customize [
                        "modifyvm", :id,
                        "--memory", "1024",
                        "--cpus", "2"]
        end
        node2.vm.network :private_network, ip: "192.168.200.5"
        node2.vm.hostname = "node2"
        node2.vm.provision :shell, path: "scripts/setup-hosts.sh"
        node2.vm.provision :shell, path: "scripts/setup-node.sh"
        node2.vm.provision :shell, path: "scripts/installNode.sh"
    end

    config.vm.define "nodemaster" do |nodemaster|
        nodemaster.vm.boot_timeout   = 9000
        nodemaster.vm.box = "bento/ubuntu-22.04"
        nodemaster.vm.provider "virtualbox" do |v|
          v.customize ["modifyvm", :id, "--memory", "1024"]
        end
        nodemaster.vm.network :private_network, ip: "192.168.200.3"
        nodemaster.vm.hostname = "nodemaster"
        nodemaster.vm.provision :shell, path: "scripts/setup-hosts.sh"
        nodemaster.vm.provision :shell, path: "scripts/setup-master.sh"
        nodemaster.vm.provision :shell, path: "scripts/installMaster.sh"
    end

end
