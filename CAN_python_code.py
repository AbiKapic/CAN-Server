import threading
import can
import json
import paho.mqtt.client as mqtt




# postavke za mqtt
broker_za_mqtt = 'broker.hivemq.com'
port_za_mqtt = 1883
tema_za_can_mqtt = 'can/poruke'  # Topic for CAN to MQTT
tema_za_mqtt_can = 'mqtt/poruke'  # Topic for MQTT to CAN




# postavke za can preko virtuelnog dijela
interfejs_za_can = 'vcan0'  # tip cana
tip_busa_za_can = 'socketcan'  # u ovom slučaju virtuelno okruženje preko wsl2 socketcan




# možemo postaviti odmah can bus
bus = can.interface.Bus(channel=interfejs_za_can, bustype=tip_busa_za_can)





def can_na_mqtt():
   # thread funkcija koja će služiti za poruke preko cana na mqtt
    klijent_za_mqtt = mqtt.Client()

    def kad_se_poveze_za_mqtt(client, userdata, flags, rc):
        print(f"Povezano sa brokerom za MQTT sa kodom {rc}")
        print("Ovaj prijenos će biti za slanje poruka sa CAN na MQTT")

    # postaviti mqtt klijenta za slanje poruka sa CAN na MQTT
    klijent_za_mqtt.on_connect = kad_se_poveze_za_mqtt
    klijent_za_mqtt.connect(broker_za_mqtt, port_za_mqtt)
    klijent_za_mqtt.loop_start()  # započeti petlju za klijenta

    while 1:
       
        poruka = bus.recv()  # primi can poruku sa bus.recv()
        if poruka:
                
            poruka_rjecnik = {
                'arbitracijski_id': poruka.arbitration_id,
                'podaci': list(poruka.data),
                'da_li_je_id_extendovan': poruka.is_extended_id,
                'da_li_je_can_fd': poruka.is_fd,
                'da_li_je_greska': poruka.is_error_frame,
                'vremenska_oznaka': poruka.timestamp
                
            }
                
            poruka_u_json = json.dumps(poruka_rjecnik) # konvertovati u poruku jsona

                
            klijent_za_mqtt.publish(tema_za_can_mqtt, poruka_u_json)
            print(f"Poruka poslana sa CAN-a na MQTT: {poruka_u_json}")
            print(f"Duzina podataka: {len(poruka.data)}")
       






def mqtt_na_can():
    
    
    # threadovana funkcija koja će slati poruke sa MQTTa na CAN
    def kad_se_poveze_za_can(client, userdata, flags, rc):
        print(f"Povezano sa brokerom za MQTT sa kodom {rc}")
        print("Ovaj prijenos će biti za slanje poruka sa MQTT na CAN")
        client.subscribe(tema_za_mqtt_can)  # subskrajbuj se na temu za slanje poruka mqtt na can



    def kad_se_dobije_poruka(client, userdata, msg):
        poruka = msg.payload.decode()
        print(f"Poslana MQTT poruka na CAN: {poruka}")

        # sad rastaviti poruku iz jsona
        poruka_iz_jsona = json.loads(poruka)
        id_za_can = poruka_iz_jsona.get('arbitracijski_id')
        podatak_za_can = poruka_iz_jsona.get('podaci')
        da_li_je_id_extendovan = poruka_iz_jsona.get('da_li_je_id_extendovan', False)
        da_li_je_can_fd = poruka_iz_jsona.get('da_li_je_can_fd')
        da_li_je_greska = poruka_iz_jsona.get('da_li_je_greska')
        vremenska_oznaka = poruka_iz_jsona.get('vremenska_oznaka')
           


        # postavi i posalji can poruku
        poruka_za_can = can.Message(
            arbitration_id=int(id_za_can),
            data=bytes(podatak_za_can),
            is_extended_id=da_li_je_id_extendovan,
            is_fd = da_li_je_can_fd,
            is_error_frame=da_li_je_greska,
            timestamp=vremenska_oznaka
            
            
        )
        bus.send(poruka_za_can)
        print(f"Poslana poruka je: : ID={id_za_can}, Podatak={bytes(podatak_za_can).hex()}, Ekstendovan={da_li_je_id_extendovan}, FD={da_li_je_can_fd}, GRESKA={da_li_je_greska}, VREMENSKA_OZNAKA={vremenska_oznaka}")
      

    # postavi klijenta za mqtt
    klijent_za_mqtt = mqtt.Client()
    klijent_za_mqtt.on_connect = kad_se_poveze_za_can
    klijent_za_mqtt.on_message = kad_se_dobije_poruka

    # povezi se brokerom
    klijent_za_mqtt.connect(broker_za_mqtt, port_za_mqtt)
    
    
    
    
    klijent_za_mqtt.loop_forever()  # pocni petlju za mqtt klijenta



# zapoceti ova 2 threada
thread_za_can_na_mqtt = threading.Thread(target=can_na_mqtt, daemon=True)
thread_za_mqtt_na_can = threading.Thread(target=mqtt_na_can, daemon=True)


thread_za_can_na_mqtt.start()
thread_za_mqtt_na_can.start()


def main():
    thread_za_can_na_mqtt.join()  # dok ovaj thread zavrsi treba sacekati
    thread_za_mqtt_na_can.join()   # zatim ovaj
    bus.shutdown()     # mora se na kraju ugasiti bus za CAN, inace pravi problem
    
if __name__ == '__main__':
    main()

