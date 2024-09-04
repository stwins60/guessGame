pipeline {
    agent any

    environment {
        IMAGE_NAME = "idrisniyi94/guess-game:v.0.0-${env.BUILD_NUMBER}-lite"
        DOCKERHUB_CREDENTIALS = credentials('f81abbea-2b04-4323-9b98-5964dfd2af75')
    }

    stages {
        stage("Clean Workspace") {
            steps {
                cleanWs()
            }
        }
        stage("Git Checkout") {
            steps {
                checkout scmGit(branches: [[name: '*/master']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/stwins60/guessGame.git']])
            }
        }
        stage("Docker Login") {
            steps {
                script {
                    sh "echo $DOCKERHUB_CRENDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin"
                }
            }
        }
        stage("Build Docker Image") {
            steps {
                script {
                    sh "docker build -t $IMAGE_NAME ."
                }
            }
        }
        stage("Push to DockerHub") {
            steps {
                script {
                    sh "docker push $IMAGE_NAME"
                }
            }
        }
        stage("Deploy to K8S") {
            steps {
                script {
                    dir('./k8s') {
                        withKubeCredentials(kubectlCredentials: [[caCertificate: '', clusterName: '', contextName: '', credentialsId: '88a9f11c-11e5-4bdb-b3bd-f63dba417648', namespace: '', serverUrl: '']]) {
                            sh "sed -i 's|IMAGE_NAME|$IMAGE_NAME|g' deploy.yaml"
                            sh "kubectl apply -f ."
                            echo "Deployed.. Check the namespace"
                        }
                    }
                }
            }
        }
    }
}