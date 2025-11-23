# **Отчёт по домашнему заданию (Часть B: Zabbix)**

## **1. Запуск окружения**

Стек был поднят командой:

```bash
cd partB
docker compose up -d
```

После запуска сервисы были доступны:

* Zabbix Web: [http://localhost:8085](http://localhost:8085) (Admin/zabbix)
* Zabbix Server
* Zabbix Agent2 (`zabbix-agent2`)
* Postgres для Zabbix

---

## **2. Добавление хоста в Zabbix**

В **Configuration → Hosts → Create host** был создан новый хост:

* **Host name:** `docker-agent`
* **Host group:** `docker`
* **Template:** `Linux by Zabbix agent`
* **Interface:**

  * Type: Agent
  * Connect to: **DNS**
  * DNS name: `zabbix-agent2`
  * Port: `10050`

⚠ Изначально интерфейс был настроен как `IP: 127.0.0.1`, из-за чего passive item’ы были в состоянии *no data*.
После переключения на **DNS + zabbix-agent2** метрики начали корректно поступать.

---

## **3. Проверка поступления метрик**

В разделе:

**Monitoring → Latest data → Host: docker-agent**

проверено:

* CPU load
* CPU utilization
* Memory usage
* Filesystem usage
* Network metrics
* Agent availability

Метрики обновляются каждые 5–15 секунд — хост корректно собирает данные.

---

## **4. Создание нагрузки и генерация проблемы**

Для проверки триггеров была создана **реальная CPU-нагрузка** внутри контейнера агента:

```bash
docker exec -it zabbix-agent2 sh -c \
'yes > /dev/null & yes > /dev/null & yes > /dev/null & sleep 600'
```

Это подняло CPU >600% (видно в Docker stats).

---

## **5. Создание собственного триггера**

В разделе:

**Configuration → Hosts → docker-agent → Triggers → Create trigger**

создан тестовый триггер:

* **Name:** `Test CPU load > 5%`
* **Severity:** Warning
* **Expression:**

```text
{docker-agent:system.cpu.load[percpu,avg1].last()}>0.1
```

Выражение собрано через Expression Constructor → гарантированно привязано к реальному item’у.

---

## **6. Получение события в Problems**

После включения нагрузки и обновления фильтра:

**Monitoring → Problems → Host: docker-agent**

появилось событие:

```
Test CPU load > 5%
```

Проблема отображалась красным/желтым цветом в зависимости от severity.

Для снятия нагрузки было выполнено:

```bash
docker exec -it zabbix-agent2 pkill yes
```

Через несколько секунд триггер перешёл в состояние **OK**, что подтверждает корректную работу событийной модели.

---

## **7. Дополнительная проблема по доступности агента**

В процессе настройки наблюдалась проблема:

```
Linux: Zabbix agent is not available (for 3m)
```

Она возникла из-за неправильного интерфейса (`127.0.0.1`).
После исправления и перевода на `DNS + zabbix-agent2` проблема ушла в OK — система стала получать данные.

---

## **8. Завершение работы**

Стек корректно остановлен командой:

```bash
cd partB
docker compose down -v
```

---

# **Итог**

* Хост добавлен и корректно связан по DNS.
* Метрики собираются, графики строятся.
* Создан собственный триггер.
* Сгенерирована реальная CPU-проблема и зафиксирована в Monitoring → Problems.
* Проблема устранена и перешла в OK.
* Домашнее задание выполнено полностью.

---

