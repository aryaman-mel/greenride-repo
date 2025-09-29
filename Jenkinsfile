pipeline {
  agent any

  environment {
    IMAGE  = 'docker.io/aryaman124/greenride-repo'
    TAG    = "${BUILD_NUMBER}"
    CREDS  = 'dockerhub-creds'
  }

  options {
    skipDefaultCheckout(true)
    timestamps()
  }

  stages {
    stage('Checkout SCM') {
      steps {
        checkout scm
      }
    } // Checkout

    stage('Build') {
      steps {
        sh """
          docker build -t ${IMAGE}:${TAG} .
        """
      }
    } // Build

    stage('Test') {
      steps {
        sh '''
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          pip install -r app/requirements.txt
          pytest -q --cov=app --cov-report xml:coverage.xml tests --rootdir=.
        '''
      }
    } // Test

    stage('Code Quality') {
      steps {
        sh '''
          . .venv/bin/activate
          flake8 app tests
        '''
      }
    } // Code Quality

    stage('Security') {
      steps {
        sh '''
          . .venv/bin/activate
          bandit -q -r app || true
          pip-audit -f cyclonedx -o sbom.json || true
          safety check || true
        '''
      }
    } // Security

    stage('Push Image') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(credentialsId: CREDS, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh """
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
            docker tag ${IMAGE}:${TAG} ${IMAGE}:latest
            docker push ${IMAGE}:${TAG}
            docker push ${IMAGE}:latest
          """
        }
      }
    } // Push

    stage('Deploy: Staging') {
      when { branch 'main' }
      steps {
        sh 'docker compose -f docker-compose.staging.yml up -d --force-recreate'
      }
    } // Staging

    stage('Release: Prod Gate') {
      when { branch 'main' }
      steps {
        input message: 'Promote to production?', ok: 'Release'
      }
    } // Gate

    stage('Deploy: Production') {
      when { branch 'main' }
      steps {
        sh 'docker compose -f docker-compose.prod.yml up -d --force-recreate'
      }
    } // Prod

    stage('Monitoring & Alerting') {
      steps {
        echo 'Checking health & notifying…'
        sh 'curl -fsS http://localhost:8081/health || true'
      }
    } // Monitoring
  } // stages

  post {
    always {
      archiveArtifacts artifacts: 'coverage.xml, sbom.json', allowEmptyArchive: true
      junit allowEmptyResults: true, testResults: 'pytest.xml'
    }
    success {
      echo "Done: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
    }
    failure {
      echo "Build failed. See console for details."
    }
  } // post
} // pipeline
