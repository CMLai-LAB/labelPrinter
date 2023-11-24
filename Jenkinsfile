pipeline {
    agent any
    stages {
        stage('Setting up the workspace') {
            steps {
                cleanWs()
            }
        }
        stage('Build and Push the docker image') {
            steps {
                sh 'docker build . -t labelprinter:latest --no-cache'
            }
        }
    }
}
