pipeline {
    agent any
    stages {
        stage('Build and Push the docker image') {
            steps {
                sh 'docker build . -t labelprinter:latest --no-cache'
            }
        }
    }
}
