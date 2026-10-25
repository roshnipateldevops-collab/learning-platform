pipeline {
    agent any

    environment {
        IMAGE       = "roshni1911/learning-platform"
        SSH_KEY     = "/var/lib/jenkins/.ssh/prt-key"
        DB_HOST     = "10.0.1.162"
        DB_PASSWORD = "Learn@123"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/roshnipateldevops-collab/learning-platform.git'
            }
        }

        stage('Build & Validate') {
            steps {
                sh 'python3 -m py_compile app.py && echo "Syntax check passed"'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t $IMAGE:$BUILD_NUMBER -t $IMAGE:latest .'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker push $IMAGE:$BUILD_NUMBER
                        docker push $IMAGE:latest
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to App Servers') {
            steps {
                script {
                    def servers = ['app1': '100.29.183.73', 'app2': '100.54.117.28']
                    servers.each { name, ip ->
                        sh """
                            ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ubuntu@${ip} '
                                docker pull ${IMAGE}:${BUILD_NUMBER} &&
                                (docker rm -f learning-app || true) &&
                                docker run -d --name learning-app --restart always \
                                  -p 127.0.0.1:5000:5000 \
                                  -e DB_HOST=${DB_HOST} \
                                  -e DB_NAME=learning_db \
                                  -e DB_USER=learning_user \
                                  -e DB_PASSWORD=${DB_PASSWORD} \
                                  -e APP_SERVER=${name} \
                                  ${IMAGE}:${BUILD_NUMBER}
                            '
                        """
                    }
                }
            }
        }

        stage('Verify') {
            steps {
                script {
                    ['100.29.183.73', '100.54.117.28'].each { ip ->
                        sh """
                            ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ubuntu@${ip} '
                                docker ps --filter name=learning-app --format "{{.Names}} {{.Image}} {{.Status}}"
                                for i in 1 2 3 4 5 6 7 8 9 10; do
                                    curl -sf http://localhost/health && exit 0
                                    sleep 3
                                done
                                exit 1
                            '
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            sh 'docker image prune -f || true'
        }
        success {
            echo "Deployed build ${BUILD_NUMBER} to both app servers"
        }
    }
}
