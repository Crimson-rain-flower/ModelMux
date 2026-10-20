pipeline {
    agent any
    parameters {
        booleanParam(name: 'BREAK_MODEL', defaultValue: false,
                     description: 'Deliberately regress the light model')
    }
    environment {
        PATH = "${WORKSPACE}\\venv\\Scripts;${env.PATH}"
        BREAK = "${params.BREAK_MODEL ? '1' : '0'}"
    }
    stages {
        stage('Setup') {
            steps { bat 'python -m venv venv && pip install -q -r requirements-dev.txt' }
        }
        stage('Lint') {
            steps { bat 'flake8 . --exclude venv,docs --max-line-length 100' }
        }
        stage('Unit Tests') {
            steps { bat 'pytest -q tests' }
        }
        stage('Train Models') {
            steps { bat 'python train.py' }
        }
        stage('Model Quality Gate') {
            steps { bat 'python validate_models.py' }
        }
        stage('Build Images') {
            steps { bat 'docker compose build' }
        }
        stage('Deploy') {
            steps { bat 'docker compose up -d' }
        }
        stage('Smoke Test') {
            steps { bat 'python smoke_test.py' }
        }
        stage('Resilience Test') {
            steps {
                bat 'docker compose stop model-heavy'
                bat 'python smoke_test.py degraded'
                bat 'docker compose start model-heavy'
                bat 'ping -n 6 127.0.0.1 > nul'
            }
        }
        stage('Cost Benchmark') {
            steps { bat 'python benchmark.py' }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'benchmark.md, models/metrics.json',
                             allowEmptyArchive: true
        }
        failure {
            bat 'docker compose logs --tail=40 || exit 0'
        }
    }
}
