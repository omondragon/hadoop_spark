# hadoop_spark

Este repositorio contiene un cluster funcional Hadoop/Spark con una aplicacion
aprovisionada que implementa algoritmos de vision computacional para conteo de vehiculos 
y deteccion  de velocidad. Dicho algoritmo esta escrito en python y
usa OpenCV. El cluster esta conformado por dos maquinas virtuales
que corresponden a un node maestro (nodemaster) y dos nodos de datos (node1, node2) hadoop.

# Cómo usar este repositorio

1. Descargar e instalar VirtualBox desde https://www.virtualbox.org/wiki/Downloads

2. Descargar e instalar Vagrant desde https://developer.hashicorp.com/vagrant/downloads

3. Ejecutar ```vagrant up``` para crear las tres maquinas virtuales

4. Ejecutar 
```
vagrant ssh node1
vagrant ssh node2 o 
vagrant ssh nodemaster 
```
para ingresar a las maquinas virtuales

# Correr aplicación de prueba

1. Conectarse al nodemaster
```
vagrant ssh nodemaster
```
2. Cambiar a usuario hadoop
```
su hadoop
```
El password solicitado es hadoop

3. [Opcional] Si ha apagado o reiniciado las máquinas previamente debe iniciar yarn y HDFS
```
start-dfs.sh
start-yarn.sh
```
4. Verifique los nodeos activos
```
yarn node -list
2023-01-13 15:23:52,862 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at nodemaster/192.168.200.3:8032
Total Nodes:2
         Node-Id	     Node-State	Node-Http-Address	Number-of-Running-Containers
     node1:46471	        RUNNING	       node1:8042	                           0
     node2:44645	        RUNNING	       node2:8042	                           0
```

5. Subir video de prueba al sistema de archivos distribuido (HDFS)
```
cd /vagrant/media
hadoop@nodemaster:/vagrant/media$  hdfs dfs -ls
hdfs dfs -put corto30s1.mov  vids
hdfs dfs -put corto30s3.mov  vids
hdfs dfs -ls vids
```
4. Ejecutar aplicacion de conteo vehicular
```
cd /vagrant/src
hadoop@nodemaster:/vagrant/src$ ./run_traffic.sh 
```
5. Los videos resultantes estaran en la carpeta /tmp del node1.

Ejecutar:
```
ssh node1
cd /tmp
ls
```
El nombre del video original tendra un prefijo "ori" y el del resultante un
prefijo "rs". Por ejemplo,
```
ori-4841c4fc-f3f9-11e8-8f7b-0800275f82b1.mp4
rs-4841c4fc-f3f9-11e8-8f7b-0800275f82b1.avi
```
Para extraer estos videos los puede copiar al directorio sincronizado de Vagrant

Por ejemplo:
```
cp /tmp/ori-4841c4fc-f3f9-11e8-8f7b-0800275f82b1.mp4  /vagrant/ori-4841c4fc-f3f9-11e8-8f7b-0800275f82b1.mp4
cp /tmp/ori-4841c4fc-f3f9-11e8-8f7b-0800275f82b1.mp4 /vagrant/rs-4841c4fc-f3f9-11e8-8f7b-0800275f82b1.avi
```
De esta manera los videos quedaran disponibles en el directorio raiz del proyecto
en la maquina anfitriona.
