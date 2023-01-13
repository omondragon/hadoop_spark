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
Verifique el dashboard de Hadoop en ```http://192.168.200.3:8088/cluster```

4. Verifique los nodeos activos usando ``` yarn node -list ```. Debe obtener una salida como:
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
6. Ejecutar aplicacion de conteo vehicular
```
cd /vagrant/src
hadoop@nodemaster:/vagrant/src$ ./run_traffic.sh 
```
Debe obtener una respuesta como:
```
23/01/13 15:55:33 INFO Client: 
	 client token: N/A
	 diagnostics: N/A
	 ApplicationMaster host: node2
	 ApplicationMaster RPC port: 46465
	 queue: default
	 start time: 1673625230579
	 final status: SUCCEEDED
	 tracking URL: http://nodemaster:8088/proxy/application_1673623197464_0001/
	 user: hadoop
23/01/13 15:55:33 INFO ShutdownHookManager: Shutdown hook called
23/01/13 15:55:33 INFO ShutdownHookManager: Deleting directory /tmp/spark-5046cd61-80bb-4b65-9424-7fb96c8b7081
23/01/13 15:55:33 INFO ShutdownHookManager: Deleting directory /tmp/spark-3461053a-3edc-4dc3-ab1e-5c6ff377030f
```

5. Los videos resultantes estaran en la carpeta /tmp de uno de los nodos. Puede verificar el nodo asignado en el dashboard de Hadoop en ```http://192.168.200.3:8088/cluster```

Para verificar en el nodo 1, ejecutar:
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
