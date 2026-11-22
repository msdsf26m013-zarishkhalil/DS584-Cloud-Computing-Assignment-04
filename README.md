# EMI Calculator - Cloud Computing Assignment 04

## Project Overview
A cloud-native Loan EMI Calculator deployed on Kubernetes (Minikube), using MongoDB as a replicated database. The application supports EMI calculation, calculation history, health monitoring, load balancing, rolling updates, and automatic scaling.

## Technologies Used
- Node.js
- Docker
- Kubernetes
- Minikube
- MongoDB Replica Set
- NGINX Ingress
- Horizontal Pod Autoscaler (HPA)
- Python

## Project Structure
- `app/` - Web application source code and Docker configuration.
- `k8s/` - Kubernetes deployment, MongoDB, service, ingress, and HPA manifests.
- `scripts/` - Performance testing, staged load testing, and monitoring scripts.
- `results/` - Experiment CSV files, test logs, and generated graphs.

## Application Features
- Loan EMI calculation.
- Total payment and total interest calculation.
- Calculation history using MongoDB.
- Application health endpoint.
- Pod name and IP in calculation responses.
- MongoDB replica set with three members.
- Kubernetes load balancing and self-healing.
- Rolling update and rollback.
- CPU-based horizontal pod autoscaling.

## Deployment
The application is containerized using Docker and deployed on a Minikube Kubernetes cluster.

Kubernetes manifests are available in the `k8s/` directory.

## Performance Evaluation
Performance experiments were conducted at different request rates and replica counts. Monitoring data and generated graphs are available in `results/`.

## Repository Contents
This repository contains the application source code, Docker configuration, Kubernetes manifests, test scripts, experiment results, and graphs.

