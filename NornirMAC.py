from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
import yaml, os

templates = os.path.dirname(os.path.abspath(__file__)) + '\\ntc-template\\templates\\'
os.environ['NET_TEXTFSM']= templates

nr = InitNornir(config_file="config.yaml")
res_sia  = nr.run(netmiko_send_command, command_string="show ip arp", use_textfsm=True)
res_smat = nr.run(netmiko_send_command, command_string="show mac address-table", use_textfsm=True)
res_sis  = nr.run(netmiko_send_command, command_string="show interface switchport", use_textfsm=True)

with open('input_macs.yaml') as f: MAC_S = yaml.safe_load(f)                                                         # Загружаем список MAC-адресов для поиска из файла input_macs.yaml

for dev in res_sia.keys():                                                                                           # Для всех устройств
    for dev_attr in res_sia[dev][0].result:                                                                          # разбираем каждую строку "show ip arp"
        if dev_attr["mac"] in MAC_S and dev_attr["age"] == "-":                                                      # и ищем совпадение с любым элементом MAC_S + (у MAC интерфейса age нет)   
            print("MAC {} belongs to device '{}' SVI {}".format(dev_attr["mac"], dev, dev_attr["interface"]))        # Если таковое найдено - отображаем данные устройства и SVI

for dev in res_smat.keys():                                                                                          # Для всех устройств
    for dev_attr in res_smat[dev][0].result:                                                                         # разбираем каждую строку "show mac address-table"
        if dev_attr["destination_address"] in MAC_S:                                                                 # и ищем совпадение с любым элементом MAC_S  
          if_ind = [n for n,x in enumerate(res_sis[dev][0].result) if x["interface"]==dev_attr["destination_port"]]  # Если таковое найдено - находим индекс соответствующего интерфейса в res_sis
          if len(if_ind) == 1:                                                                                       # .. и если таковой индекс существует
            if_params = res_sis[dev][0].result[if_ind[0]]                                                            # .. и получам набор его параметро по структуре res_sis
            if (if_params["mode"] == "static access") and (if_params["access_vlan"] == dev_attr["vlan"]):            # .. Если этот порт активный + в режиме access + (это не дубль от voice_vlan)
              print("MAC {} was learned on device '{}' access port {}".format(                                       # .. отображаем данны соответствующего устройства и интерфейса
                  dev_attr["destination_address"], dev, dev_attr["destination_port"]))   