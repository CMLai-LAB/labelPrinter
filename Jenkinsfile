pipeline {
    agent any
    stages {
        stage('Build the docker image inside minikube docker insntance') {
            steps {
                sh 'eval $(minikube docker-env)'
                sh 'docker build . -t labelprinter:latest --no-cache'
            }
        }

        stage('Deploy to the minikube') {
            steps {
                dir('deployment') {
                    sh 'kubectl apply -f deployment.yaml'
                    sh 'kubectl apply -f labelPrinter-Svc.yaml'
                }
            }
        }

    }
}
