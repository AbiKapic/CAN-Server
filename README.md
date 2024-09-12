# Can-Server

#Abdulah Kapić - Can Server  
Slanje CAN poruka na MQTT i obrnuto ( virtuelno generisanje poruka )  
Korišten je MQTTX za MQTT i primanje i slanje poruka na ili sa CAN-a  
Simulacija je urađena preko WSL2 / Ubuntu  
"Customized" Linux kernel za windows korisnike koji podržava CAN utils  
Korištene komande sa Ubuntu-a su cangen vcan0 za generisanje CAN poruka  
Isto tako candump vcan0 za primanje poruka na CAN  
Kreirane teme na MQTTx dvije, jedna za slanje poruka sa MQTTa a druga za primanje poruka sa CAN-a  
