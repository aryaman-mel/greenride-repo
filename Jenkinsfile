pipeline {
  agent any
  environment {
    APP_NAME = 'greenride'
    REGISTRY = 'docker.io/aryaman124'
    IMAGE = "${REGISTRY}/${APP_NAME}"
    TAG = "${env.BUILD_NUMBER}"
  }
  options { timestamps() }

  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Build') {
      steps { sh 'docker build -t ${IMAGE}:${TAG} .' }
    }

    stage('Test') {
    steps {
        sh '''#!/bin/bash
        set -euo pipefail
        python3 -m venv .venv
        . .venv/bin/activate
        pip install --upgrade pip
        pip install -r app/requirements.txt
        pytest -q --cov=app --cov-report xml:coverage.xml tests --rootdir=.
        '''
    }
}

    stage('Code Quality') {
      steps {
        sh '''
          pip install flake8
          flake8 app
        '''
      }
    }

    stage('Security') {
      steps {
        sh '''
          pip install bandit pip-audit
          bandit -r app -f txt -o bandit.txt || true
          pip-audit -r app/requirements.txt -f json -o pip_audit.json || true
          echo "== Bandit summary ==" && head -n 50 bandit.txt || true
          echo "== pip-audit summary ==" && wc -l pip_audit.json || true
        '''
      }
    }

    stage('Push Image') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                          usernameVariable: 'DOCKER_USER',
                                          passwordVariable: 'DOCKER_PASS')]) {
          sh '''
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
            docker tag ${IMAGE}:${TAG} ${IMAGE}:staging
            docker push ${IMAGE}:${TAG}
            docker push ${IMAGE}:staging
          '''
        }
      }
    }

    stage('Deploy: Staging') {
      steps {
        sh '''
          export REGISTRY=${REGISTRY}
          export TAG=staging
          docker compose -f docker-compose.staging.yml up -d
          sleep 3
          curl -sf http://localhost:8081/health
        '''
      }
    }

    stage('Release: Prod Gate') {
      when { branch 'main' }
      steps {
        input message: 'Promote to production?', ok: 'Release'
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                          usernameVariable: 'DOCKER_USER',
                                          passwordVariable: 'DOCKER_PASS')]) {
          sh '''
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
            docker tag ${IMAGE}:${TAG} ${IMAGE}:prod
            docker push ${IMAGE}:prod
          '''
        }
      }
    }

    stage('Deploy: Production') {
      when { branch 'main' }
      steps {
        sh '''
          export REGISTRY=${REGISTRY}
          export TAG=prod
          docker compose -f docker-compose.prod.yml up -d
          sleep 3
          curl -sf http://localhost/health
        '''
      }
    }

    stage('Monitoring & Alerting') {
      steps {
        script {
          try {
            sh 'curl -sf http://localhost/health'
            echo 'Health OK'
          } catch (e) {
            echo 'Health check failed'
            error('Monitoring stage failed')
          }
        }
      }
    }
  }

  post {
    always { echo "Done: ${env.JOB_NAME} #${env.BUILD_NUMBER}" }
  }
}
