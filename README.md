# Repository Context Analyser

## Overview

The `repo-context-analyser` repository hosts a collection of tools and GitHub Actions workflows designed to automate and enhance CI/CD processes across multiple projects. It provides reusable scripts and workflows that perform various analysis and reporting tasks.

## Features

- **Reusable CI Workflows**: Centralized GitHub Actions workflows to promote consistency and efficiency in CI processes across multiple projects.
- **Comprehensive Analysis Scripts**: Includes Python scripts for parsing Docker images, analyzing dependencies, and generating security and compliance reports.

## Workflow Description

### CI Pipeline Workflow

The main workflow includes several tasks:

1. Setting up a Python environment.
1. Installing necessary dependencies.
1. Executing multiple Python scripts to:
   - Parse Docker images.
   - Analyze image dependencies.
   - Fetch detailed image information from Docker Hub.
   - Identify programming languages in repositories.
   - Perform security and compliance checks.
   - Generate dependency and compliance reports.
1. Comment on pull requests with the results of these analyses.

### Triggering Workflows

Workflows in this repository can be initiated in two primary ways:

- **Pull Requests**: Automatically triggers on pull requests to the `main` branch.
- **Manual Dispatch**: Available for manual activation through the GitHub Actions interface.

## Usage

### Using Workflows in Other Repositories

To utilize the workflows from this repository in another repository, include the following in your GitHub Actions workflow file:

```yaml
jobs:
  trigger-central-workflow:
    uses: Max3kkk/repo-context-analyzer/.github/workflows/ci-pipeline.yml@main
    secrets:
      MY_GITHUB_TOKEN: ${{ secrets.MY_GITHUB_TOKEN }}
```
