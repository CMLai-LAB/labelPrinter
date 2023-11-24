pipeline {
    agent any
    stages {
        stage('Checkout the repo') {
            steps {
                cleanWs()
                sh 'git clone git@github.com:CMLai-LAB/labelPrinter.git'
            }
        }
        stage('Build and Push the docker image') {
            steps {
                dir('labelPrinter') {
                    sh 'docker build . -t labelprinter:latest --no-cache'
                }
            }
        }
    }
}
