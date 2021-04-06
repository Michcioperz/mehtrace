pipeline {
  agent any
  stages {
    stage('Check Clippy lints') {
      parallel {
        stage('Clippy') {
          steps {
            sh '''


cargo +nightly clippy --workspace --all-targets --all-features -- -D warnings

'''
          }
        }

        stage('Check formatting') {
          steps {
            sh 'cargo +stable fmt --all -- --check'
          }
        }

        stage('Run tests') {
          steps {
            sh 'cargo +stable test --workspace'
          }
        }

        stage('Build documentation') {
          steps {
            sh 'cargo +stable doc --workspace --all-features'
          }
        }

      }
    }

  }
}