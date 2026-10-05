// Adaptacao da esteira V5.1 da professora para o laboratorio A2 Linux.
// O mesmo arquivo executa as Praticas 2 e 3, carregado via SCM.
def maven(String args) {
    sh 'export JAVA_HOME="$JAVA_HOME_17_X64"; export PATH="$JAVA_HOME/bin:$PATH"; chmod +x mvnw; ./mvnw ' + args
}
pipeline {
    agent any
    options { skipDefaultCheckout(true); timeout(time: 35, unit: 'MINUTES'); timestamps() }
    environment {
        COMPOSE_FILE = 'docker-compose.homol.yml'
        COMPOSE_PROJECT_NAME = 'a2homol'
        DOCKER_IMAGE = 'jogo-enigma-api'
        IMAGE_TAG = "${BUILD_NUMBER}"
        API_PORT = '8080'
        PROMETHEUS_PORT = '9091'
    }
    stages {
        stage('Checkout') { steps { checkout scm; sh 'git rev-parse HEAD; docker version; docker compose version' } }
        stage('JUnit + JaCoCo') {
            steps { script { maven('-B clean test') } }
            post { always {
                junit 'target/surefire-reports/*.xml'
                publishHTML(target: [reportDir:'target/site/jacoco',reportFiles:'index.html',reportName:'JaCoCo',keepAll:true,alwaysLinkToLastBuild:true,allowMissing:true])
            } }
        }
        stage('PMD') { steps { script { maven('-B pmd:pmd -DskipTests') } } }
        stage('Package') { steps { script { maven('-B package -DskipTests') } } }
        stage('Docker Build') { steps { sh 'docker compose -f "$COMPOSE_FILE" build api bff' } }
        stage('Deploy HOMOL') { steps { sh 'docker compose -f "$COMPOSE_FILE" up -d postgres pgadmin api bff prometheus grafana' } }
        stage('Health Check') { steps { sh 'python3 ci/verify.py health' } }
        stage('Cypress E2E') {
            steps { sh 'docker compose -f "$COMPOSE_FILE" --profile e2e run --rm cypress' }
            post { always { junit testResults:'frontend/cypress/results/*.xml',allowEmptyResults:true } }
        }
        stage('Observabilidade') { steps { sh 'python3 ci/verify.py metrics; docker compose -f "$COMPOSE_FILE" ps' } }
    }
    post { always {
        archiveArtifacts artifacts:'target/site/**,target/surefire-reports/**,frontend/cypress/results/**,frontend/cypress/screenshots/**,frontend/cypress/videos/**,evidence/**',allowEmptyArchive:true
    } }
}
