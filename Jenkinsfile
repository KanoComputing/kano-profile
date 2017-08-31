#!/usr/bin/env groovy

@Library('kanolib')
import build_deb_pkg


def git_clone(String repo, String branch) {
    checkout changelog: false,
        poll: false, scm: [
            $class: 'GitSCM',
            branches: [[name: branch]],
            doGenerateSubmoduleConfigurations: false,
            extensions: [[
                $class: 'RelativeTargetDirectory',
                relativeTargetDir: repo
            ]],
            submoduleCfg: [],
            userRemoteConfigs: [[
                credentialsId: '739ce9ae-b10e-4459-83c4-01a94cdbc64d',
                url: "git@github.com:KanoComputing/${repo}.git"
            ]]
        ]
}


def update_status(String context) {
    step([
        $class: 'GitHubCommitStatusSetter',
        contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: context],
        errorHandlers: [[$class: 'ChangingBuildStatusErrorHandler', result: 'FAILURE']]
    ])
}


parallel(
    'build': {
        stage ('Build') {
            // build_deb_pkg 'kano-profile', env.BRANCH_NAME, 'scratch'
            // update_status('Package build')
        }
    },
    'test': {
        stage ('Test') {
            node ('os') {
                // try {
                        git_clone 'kano-profile', env.BRANCH_NAME

                        clone_dir = sh(script: 'pwd', returnStdout: true).trim()
                        python_path = sh(script: 'echo "$PYTHONPATH"', returnStdout: true).trim()

                        for (repo in ['kano-i18n', 'kano-toolset']) {
                            git_clone repo, 'master'
                            python_path = "$clone_dir/$repo:$python_path"
                        }
                    // docker.image('kano/python-test').inside('--user kanux:test') {
                    docker.image('kano/python-test').inside() {

                        sh "cd kano-profile && SUDO_USER=kanux PYTHONPATH=$python_path make check"
                    }
                //} catch (err) {
                    // update_status('Tests')
                // }
            }
        }
    }
)
