# Модуль с примерами использования библиотеки MBee-Python для работы с модулями MBee производства фирмы "Системы, модули и компоненты" методом callback-функций.
# "Системы модули и компоненты" ("СМК"). 2018. Москва.
# Распространяется свободно. Надеемся, что программные продукты, созданные
# с помощью данной библиотеки будут полезными, однако никакие гарантии, явные или
# подразумеваемые не предоставляются.
# The MIT License(MIT)
# MBee-Python Library.
# Copyright © 2017 Systems, modules and components. Moscow. Russia.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files(the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and / or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions :
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Данный пример предназначен для демонстрации взаимодействия с модулем, работающим под управлением ПО SerialStar, с помощью callback-функций. Модуль должен быть предварительно настроен для работы
# в пакетном режиме UATR с escape-символами (AP = 2).
# Для полной проверки требуется 2 модуля. Локальный модуль может иметь произвольный собственный адрес (параметр MY), на удаленном модуле этот параметр должен быть равен 2.

import os, sys
#sys.path.append('C:\VONBOD\SYSMC\Low-Power RF\Python\MBee') 
#sys.path.append('/home/pi/myproject/python') 

from mbee import serialstar

import time
from threading import Timer

# Присваиваем имя COM-порта.
PORT = "COM15"

# Определяем битовую скорость COM-порта.
BITRATE = 9600

# Назначаем период таймера, который будет использоваться для периодической отправки пакетов удаленному модулю.
TICK_TIME = 1
events = {"TIMER_EVENTS": False}

# Создаем объект SerialStar.
mbee = serialstar.SerialStar(PORT, BITRATE)

# Устанавливаем событие срабатывания периодического таймера.
def timer_set_event():
    events["TIMER_EVENTS"] = True
    
# Обслуживание периодических событий.
def timer_service():
    #mbee.send_tx_request("00", "FFFF", "313233343536373839", options = "01") #API-frame 0x10. Широковещательный режим. Локальное и удаленное подтверждения отключены.
    #mbee.send_tx_request("01", "FFFF", "313233343536373839", options = "00") #API-frame 0x10. Широковещательный режим. Только локальное подтверждение.
    #mbee.send_tx_request("00", "0002", "313233343536373839", options = "00") #API-frame 0x10. Адресный режим. Только удаленное подтверждение.
    #mbee.send_tx_request("01", "0002", "313233343536373839", options = "00") #API-frame 0x10. Адресный режим. Как локальное, так и удаленное подтверждение.
    #mbee.send_immidiate_apply_local_at("01", "TX", "0002") #API-frame 0x07. Установка параметра TX, равным 2 с немедленным применением изменений.
    #mbee.send_immidiate_apply_local_at("01", "M1") #API-frame 0x07. Запрос параметра M1.
    #mbee.send_immidiate_apply_and_save_local_at("01", "M1", "3034") #API-frame 0x08. Установка параметра M1 равным 12340 с немедленным применением изменений и сохранением их в энергонезависимой памяти.
    #mbee.send_immidiate_apply_and_save_local_at("01", "M1") #API-frame 0x08. #API-frame 0x08. Запрос параметра M1.
    #mbee.send_queue_local_at("01", "M1", "3032") #API-frame 0x09. Помещение параметра M1, равным 12338 в очередь.
    #mbee.send_queue_local_at("01", "M1") #API-frame 0x09. Запрос параметра M1.
    #mbee.send_tx_request("01", "FFFF", "313233343536373839") # #API-frame 0x0F. Широковещательный режим. Только локальное подтверждение. Удаленное подтверждение невозможно вследствие того, что поле опций отсутствует.
    #mbee.send_remote_at("01", "0002", "04", "M1", "1964") #API-frame 0x17. #API-frame 0x17. Адресный режим. Установка на удаленном модуле параметра M1 равным 6500 с немедленным применением и без сохранения изменений. Как локальное, так и удаленное подтверждение.
    #mbee.send_remote_at("00", "0002", "04", "M1") #API-frame 0x17. Адресный режим. Запрос параметра M1 на удаленном модуле. Только удаленный ответ.
    pass

timer = Timer(TICK_TIME, timer_set_event) #Создание компонента таймера.

timer.start()


# Определение callback-функций для всех типов пакетов.
def frame_81_received(packet):
    print("Received 81-frame.")
    print(packet)

def frame_83_received(packet):
    print("Received 83-frame.")
    print(packet)
    
def frame_87_received(packet):
    print("Received 87-frame.")
    print(packet)
    
def frame_88_received(packet):
    print("Received 88-frame.")
    print(packet)
    
def frame_89_received(packet):
    print("Received 89-frame.")
    print(packet)
    
def frame_8A_received(packet):
    print("Received 8A-frame.")
    print(packet)    
    
def frame_8B_received(packet):
    print("Received 8B-frame.")
    print(packet)
    
def frame_8C_received(packet):
    print("Received 8C-frame.")
    print(packet)
    
def frame_8F_received(packet):
    print("Received 8F-frame.")
    print(packet)
    
def frame_97_received(packet):
    print("Received 97-frame.")
    print(packet)

# Регистрирация callback-фукнций для всех типов фреймов.
mbee.callback_registring("81", frame_81_received)
mbee.callback_registring("83", frame_83_received)
mbee.callback_registring("87", frame_87_received)
mbee.callback_registring("88", frame_88_received)
mbee.callback_registring("89", frame_89_received)
mbee.callback_registring("8A", frame_8A_received)
mbee.callback_registring("8B", frame_8B_received)
mbee.callback_registring("8C", frame_8C_received)
mbee.callback_registring("8F", frame_8F_received)
mbee.callback_registring("97", frame_97_received)

while(True):
    try:
        frame = mbee.run()
        if events["TIMER_EVENTS"]:
            events["TIMER_EVENTS"] = False
            timer_service()    
            timer = Timer(TICK_TIME, timer_set_event)
            timer.start()
            timer.setName("Thread-1")
        
    except Exception as exc:
        print("Script is stopping.", exc)
        break
    except KeyboardInterrupt:
        print("Script is stopping.")
        break