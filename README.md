# Домашняя работа: мониторинг и алертинг

Этот репозиторий содержит готовые Docker Compose стеки для выполнения домашнего задания по мониторингу.
Цель — собрать RED‑метрики демо‑сервиса, отобразить их в Grafana, сгенерировать алерты и показать доставку уведомлений. Опционально есть среда для лаборатории с Zabbix.

## Часть A — Prometheus, Grafana, Alertmanager

Стек описан в [`partA/docker-compose.yml`](partA/docker-compose.yml) и включает:

- **app** — демо‑сервис на FastAPI с RED‑метриками (`/metrics`) и эндпоинтом `/simulate` для создания нагрузки/ошибок.
- **prometheus** — снимает метрики и применяет правила из [`partA/prometheus/alerting/rules.yml`](partA/prometheus/alerting/rules.yml).
- **alertmanager** — отправляет все алерты в локальный webhook echo (`echo`), конфиг — [`partA/alertmanager/alertmanager.yml`](partA/alertmanager/alertmanager.yml).
- **grafana** — уже настроенная datasource и дашборд «RED Demo App» (`partA/grafana/provisioning/dashboards/red-demo.json`).
- **echo** — простой приёмник вебхуков, чтобы видеть payload Alertmanager.

### Как запустить

```bash
cd partA
docker compose up -d --build
```

Порты сервисов:

- Демо‑приложение: http://localhost:8080 (проверьте `/`, `/healthz`, `/simulate?load_ms=800&error_rate=0.5`)
- Prometheus: http://localhost:9090 (разделы **Status → Targets** и **Alerts**)
- Alertmanager: http://localhost:9093 (вкладка **Alerts**)
- Grafana: http://localhost:3000 (логин `admin` / `admin`)
- Webhook echo: http://localhost:8085 (UI показывает полученные JSON‑payload'ы)

### Как спровоцировать алерты

Используйте `/simulate`, чтобы создать нагрузку:

- **Error-rate**: запустите в цикле `curl "http://localhost:8080/simulate?error_rate=0.8&load_ms=50"` (или `watch -n0.5`). Когда доля ошибок превысит 5% за 2 минуты, сработает `HighErrorRate`.
- **Latency p95**: вызовите `curl "http://localhost:8080/simulate?load_ms=1200"`, чтобы поднять p95 выше 0.5s и вызвать `HighLatencyP95`.
- **Target down**: остановите приложение `docker compose stop app`, и через минуту сработает `DemoTargetDown`.

Проверьте статус FIRING в Prometheus (**Alerts**), убедитесь, что Alertmanager показывает алерты, и посмотрите доставленные payload'ы в echo UI.

### Завершение работы

```bash
cd partA
docker compose down -v
```

## Часть B — лаборатория Zabbix (для «отлично»)

В каталоге [`partB`](partB/README.md) — минимальная среда Zabbix (Server/Web/Agent), чтобы выполнить задания B1/B2: добавить хост, привязать шаблон и зафиксировать безопасную проблему в **Problems**.

## Где что лежит

- `partA/app/` — демо‑сервис FastAPI с метриками Prometheus.
- `partA/prometheus/` — конфиг Prometheus и правила алертов по RED.
- `partA/alertmanager/` — Alertmanager с маршрутизацией webhook на `echo`.
- `partA/grafana/` — datasource и дашборд RED для Grafana.
- `partB/` — инструкции и Compose для Zabbix (опционально).
