# tcp-over-udp
HW solution for HSE AMI nets course

---

#### Installation

requires python3.8+

```shell script
cd tcp_over_udp && python3 -m pip install -r requirements.txt
```

#### Starting Client
```shell script
./client.sh --host <host> --port <port>
```

#### Starting Server
```shell script
./server.sh --host <host> --port <port>
```

---

#### О реализации
Решение - попытка имплементировать протокол TCP поверх протокола UDP, но в сильно урезанном виде.
Пакет представляет собой вид `<header><data>`

Заголовок описывается в `tcp_over_udp/common/const.py` и занимает 13 байт. 

|Название заголовка | размер (bytes) | описание      
| ---       | ---     | ---                        
| SQN_NUMBER | 4 | собственно sequence number 
| ACK_NUMBER | 4 | собственно ack number      
| DATA_SIZE  | 2 | размер содержательной части сообщения (нужен для отделения слипшихся в буфере пакетов)
| CHECKSUM   | 2 | чексумма
| FLAGS      | 1 | Флаги пакета

Имплементация `tcp_over_udp/common/message.py`

Клиент и сервер используют общий абстрактный протокол общения, описанный в tcp_over_udp/common/protocol.py` 

Все сообщения разбиваются на пакеты по `MTU=1500`, по достижению размера отправленного сообщения в `WINDOW_SIZE`
(определяется в `tcp_over_udp/common/const.py`) с отправляющей стороны отправляется флаг PSH который на принимающей
стороне делает флаш для буфера и ACK всех уже полученных сообщений.

Таким образом скорость передачи сообщения в локальной сети в данном решении составляет 15 Mb/s

---

#### Тесты

Unit тесты поднимают локально echo сервер и клиент и проверяют корректность базовых операций

Pumba тесты поднимают docker-compose с сервером, клиентом, и контейнером/ами с пумбой
