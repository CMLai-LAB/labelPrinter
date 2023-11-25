pipeline {
    agent any
    stages {
        stage('Build the docker image inside minikube docker insntance') {
            steps {
                sh 'eval $(minikube docker-env)'
                sh 'docker build . -t 172.23.8.1:9500/labelprinter:latest --no-cache'
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
