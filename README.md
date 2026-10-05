# Atividade A2 — Jenkins CI/CD

Gustavo Champam. Laboratório acadêmico de CI, CD e observabilidade.

Base da professora: https://github.com/adleles/jogo-enigma-api-v1-A2-portavel-v5.1
A aplicação e os testes originais foram preservados. A esteira foi adaptada ao enunciado: Jenkins 9090, API 8080, BFF 3000, Prometheus 9091, Grafana 3001.

## Execução sem Docker no Windows
O workflow `.github/workflows/laboratorio.yml` fornece uma máquina Linux temporária com Docker. **Jenkins executa o Jenkinsfile**, obtido por `Pipeline script from SCM`. GitHub Actions somente prepara a máquina, inicia Jenkins e recolhe evidências reais.

Após a execução, baixe o artefato `evidencias-a2` na aba Actions. O ambiente é temporário, não um serviço público permanente. Para repetir, use Run workflow; não é preciso configurar Docker no computador pessoal.

## Pipeline único (Práticas 2 e 3)
Checkout → JUnit/Testcontainers/JaCoCo → PMD → Package → Docker Build → Deploy HOMOL → Health Check → Cypress E2E → Observabilidade.

Os testes de repository usam PostgreSQL 17 real. Cypress percorre navegador → BFF → API → PostgreSQL. PMD mantém a política didática da professora: gerar relatório sem bloquear por violações existentes; erro de execução da ferramenta interrompe o pipeline.

Dashboard provisionado: `grafana/dashboards/a2.json`. O datasource acessa `http://prometheus:9090`. Credenciais de serviços são geradas para cada laboratório e não publicadas. As portas são vinculadas apenas a localhost no runner. Nenhum push ao Docker Hub é necessário.

## Prática 1
`pratica1/` preserva o projeto https://github.com/adleles/integracao_v1. A execução Freestyle e a falha controlada estão documentadas no relatório PDF, com evidências reais de 29/09/2026.

## Repetição local em Linux com Docker
Use Java 17 e `./mvnw -B clean test`, configure as variáveis `POSTGRES_PASSWORD`, `GRAFANA_PASSWORD`, `PGADMIN_PASSWORD` e execute `docker compose -f docker-compose.homol.yml up -d --build`. Para E2E: `docker compose -f docker-compose.homol.yml --profile e2e run --rm cypress`.

## Encerramento / reversão do laboratório
`docker compose -f docker-compose.homol.yml down --remove-orphans` interrompe e remove os containers desta stack, preservando o volume PostgreSQL. O workflow descarta o runner ao terminar. Não há deploy de produção.
