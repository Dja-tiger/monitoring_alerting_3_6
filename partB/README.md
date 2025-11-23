# Часть B — быстрый старт Zabbix

Опциональный стек для выполнения заданий B1 и B2 («отлично»). Он поднимает Zabbix Server, Web UI и демонстрационный Agent с именем `docker-agent`.

## Запуск стека

```bash
cd partB
docker compose up -d
```

Доступы и порты:

- Zabbix Web: http://localhost:8081 (логин по умолчанию: `Admin` / `zabbix`)
- Порт Zabbix Server: 10051
- Порт Zabbix Agent: 10050

## B1. Добавить хост и шаблон

1. Зайдите в Zabbix Web UI → **Configuration → Hosts → Create host**.
2. Назовите хост `docker-agent`, в **Agent interfaces** укажите `zabbix-agent:10050` (DNS Docker сети).
3. В разделе **Templates** привяжите **Linux by Zabbix agent** и сохраните.
4. Откройте **Monitoring → Latest data**, чтобы убедиться, что метрики появляются.

## B2. Безопасно спровоцировать проблему

Создайте заметную ситуацию и зафиксируйте её в **Monitoring → Problems**:

- Запустите нагрузку на CPU: `docker compose exec zabbix-agent sh -c "yes > /dev/null"` на минуту, затем остановите `Ctrl+C`.
- Или временно заполните файловую систему: `docker compose exec zabbix-agent sh -c "dd if=/dev/zero of=/tmp/fill.test bs=1M count=200"`, после теста удалите файл.
- Можно также остановить агент или изменить конфиг, чтобы получить проблему доступности.

Опишите, что сделали, и приложите скриншоты **Latest data** и **Problems** для сдачи.

## Остановка

```bash
cd partB
docker compose down -v
```
