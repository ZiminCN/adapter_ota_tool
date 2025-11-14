#!bin/bash

count=1
touch record.log
while [ True  ]
do
	echo $count > record.log
	python3 ~/adapter_ota/adapter_upgrade/adapter-ota-tool/adapter_ota.py -f ~/adapter_ota/adapter_upgrade/adapter-ota-tool/D1-can-adapter-app-new.hex
	sleep 1
	python3 ~/adapter_ota/adapter_upgrade/adapter-ota-tool/adapter_ota.py -f ~/adapter_ota/adapter_upgrade/adapter-ota-tool/D1-can-adapter-app-old.hex
	count=$((count+1))
done
