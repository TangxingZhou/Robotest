#!groovy

pipeline {
  agent {
    docker {
      image '172.16.1.99/tmp/qa.tos/robot-runner'
      label 'tos_auto'
      args '--network="host" -v /tmp/caches:/tmp/caches'
    }
  }

  options {
    timeout(time: 2, unit: 'HOURS')
    retry(3)
    disableConcurrentBuilds()
    timestamps()
    buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '', daysToKeepStr: '60', numToKeepStr: '100'))
  }

  parameters {
    string(name: 'Cluster_Main_Node', defaultValue: '172.16.179.120', description: 'The main node of the TOS cluster.')
    string(name: 'Run_Tests_Arguments', defaultValue: 'tests/TOS/smoke', description: 'The arguments for robot to run tests.')
    string(name: 'Report_Email_Recipients', defaultValue: 'qualitysupport@transwarp.io,tosdev@transwarp.io', description: 'The list of recipients that will receive the report email.')
  }

  environment {
    JENKINS_USER = "root"
  }

  stages {

    stage('Run TOS Auto Tests') {
      steps {
        sh """#!/bin/bash
          ./run_tests.sh --cluster ${params.Cluster_Main_Node} --variable SEND_EMAIL:Y --variable MERGE_RESULTS:Y --rerun ${params.Run_Tests_Arguments}
        """
        step([  $class              : 'RobotPublisher',
                disableArchiveOutput: false,
                outputPath          : 'out/TOS',
                reportFileName      : 'report.html',
                outputFileName      : 'output.xml',
                logFileName         : 'log.html',
                otherFiles          : '',
                passThreshold       : 90,
                unstableThreshold   : 80
        ])
      }
    }

    stage('Send TOS Email Report') {
      steps {
        script {
          def email_report_file = 'out/TOS/email_report.html'
          def email_body=readFile(email_report_file)
          def result_color = [SUCCESS: '#27AE60', FAILURE: '#E74C3C', UNSTABLE: '#F4E242']

          def build = [
              result: "${currentBuild.currentResult}",
              color: result_color["${currentBuild.currentResult}"],
              url: "${env.BUILD_URL}",
              name: "${env.JOB_NAME}",
              date: new Date().format("EEE, dd MMM yyyy HH:mm:ss z"),
              //date: new Date(new Long("${currentBuild.startTimeInMillis}").longValue()).format("EEE, dd MMM yyyy HH:mm:ss z"),
              duration: "${currentBuild.durationString}".replace(' and counting', '')
          ]

          build.each{key, value ->
              email_body = email_body.replace("\${" + key + "}", value)
          }

          writeFile file: email_report_file, text: email_body

          emailext(
              subject: "[TOS] ${env.JOB_NAME} - ${env.BUILD_DISPLAY_NAME} - ${currentBuild.currentResult}",
              to: "${params.Report_Email_Recipients}",
              mimeType: "text/html",
              body: email_body
          )
        }
        archive(includes: 'out/TOS/**/*')
      }
    }
  }
}