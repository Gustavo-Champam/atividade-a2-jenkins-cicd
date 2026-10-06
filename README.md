# Atividade A2 — Jenkins CI/CD

Gustavo Gutierres Champam — RA 223645.
Gustavo Oliveira Camargo — RA 236024.

Laboratório acadêmico de CI, CD e observabilidade.

Base da professora: https://github.com/adleles/jogo-enigma-api-v1-A2-portavel-v5.1
A aplicação e os testes originais foram preservados. A esteira foi adaptada ao enunciado: Jenkins 9090, API 8080, BFF 3000, Prometheus 9091, Grafana 3001.

## Execução sem Docker no Windows
O workflow `.github/workflows/laboratorio.yml` fornece uma máquina Linux temporária com Docker. **Jenkins executa o Jenkinsfile**, obtido por `Pipeline script from SCM`. GitHub Actions somente prepara a máquina, inicia Jenkins e recolhe evidências reais.

Após a execução, baixe o artefato `evidencias-a2` na aba Actions. O ambiente é temporário, não um serviço público permanente. Para repetir, use Run workflow; não é preciso configurar Docker no computador pessoal.

## Pipeline único (Práticas 2 e 3)
Checkout → JUnit/Testcontainers/JaCoCo → PMD → Package → Docker Build → Deploy HOMOL → Health Check → Cypress E2E → Observabilidade.

Os testes de repository usam PostgreSQL 17 real. Cypress percorre navegador → BFF → API → PostgreSQL. PMD executa `pmd:pmd`, sem `pmd:check`, preservando a política didática de geração de relatório. Erro de execução da ferramenta interrompe o pipeline; violações são registradas no relatório.

Dashboard provisionado: `grafana/dashboards/a2.json`. O datasource acessa `http://prometheus:9090`. Credenciais de serviços são geradas para cada laboratório e não publicadas. As portas são vinculadas apenas a localhost no runner. Nenhum push ao Docker Hub é necessário.

## Prática 1
`pratica1/` preserva o projeto https://github.com/adleles/integracao_v1. A execução Freestyle e a falha controlada estão documentadas no relatório PDF, com evidências reais de 29/09/2026.

## Repetição local em Linux com Docker
Use Java 17 e `./mvnw -B clean test`, configure as variáveis `POSTGRES_PASSWORD`, `GRAFANA_PASSWORD`, `PGADMIN_PASSWORD` e execute `docker compose -f docker-compose.homol.yml up -d --build`. Para E2E: `docker compose -f docker-compose.homol.yml --profile e2e run --rm cypress`.

## Encerramento / reversão do laboratório
`docker compose -f docker-compose.homol.yml down --remove-orphans` interrompe e remove os containers desta stack, preservando o volume PostgreSQL. O workflow descarta o runner ao terminar. Não há deploy de produção.

## Entrega no modelo da professora — 06/10/2026

[PDF para entregar](entrega/Atividade_A2_MODELO_PROFESSORA.pdf) | [Word editável](entrega/Atividade_A2_MODELO_PROFESSORA.docx)

O documento preserva o modelo original e inclui os dois integrantes, 18 respostas, evidências das três práticas e a integração adicional da AC1 da equipe. Substitui o relatório anterior.

## Integração do projeto AC1 da equipe

Fonte: https://github.com/Gustavo-Champam/educacao-continuada-gamificada

O workflow `ac1.yml` inicia Jenkins e executa o job Freestyle `A2_P1_AC1_Equipe`: checkout, `mvn -B clean verify`, JUnit e JaCoCo publicados. PostgreSQL 17 real é iniciado e o teste condicional é habilitado. Resultado: 37 testes aprovados, nenhum ignorado; 100% de linhas e ramos cobertos.

[Execução AC1 aprovada](https://github.com/Gustavo-Champam/atividade-a2-jenkins-cicd/actions/runs/37479149544) | [Execução Enigma documentada](https://github.com/Gustavo-Champam/atividade-a2-jenkins-cicd/actions/runs/37337295060)
