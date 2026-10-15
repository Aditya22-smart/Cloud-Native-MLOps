# Syllabus Unit 7 & 8 Evidence: Horizontal Pod Autoscaler (HPA) Scaling Proof

**Date:** 2026-10-15  
**Environment:** GKE Zonal Cluster `pricing-staging` (`asia-south1-a`)  
**Deployment:** `pricing/pricing-api`  
**HPA Resource:** `pricing/pricing-api` (Target: 70% CPU, Min: 1, Max: 5)  

---

## 1. Initial State (Idle Baseline)

Before traffic load:
- **Replica count:** 1
- **CPU utilization:** 1% / 70%

```text
NAME                                              REFERENCE                TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/pricing-api   Deployment/pricing-api   cpu: 1%/70%   1         5         1          34m

NAME                               READY   STATUS    RESTARTS   AGE
pod/pricing-api-569485c9c4-w49st   1/1     Running   0          30m
```

---

## 2. Load Generation (High Concurrency Inference)

Executed concurrent inference traffic against the live staging endpoint (`https://pricing-staging.136.81.137.108.sslip.io/api/predict`) using `scripts/load_test_hpa.py`.

- **Traffic Target:** `POST /api/predict`
- **Concurrency:** 25 concurrent worker threads
- **Payload:** Full dynamic pricing feature vector

---

## 3. Automated Scale-Up Event (1 -> 4 -> 5 Replicas)

When incoming request volume elevated CPU usage beyond the 70% threshold (spiking to 299% - 365%), the Kubernetes Horizontal Pod Autoscaler controller automatically scaled the deployment:

```text
NAME                           CPU(cores)   MEMORY(bytes)   
pricing-api-569485c9c4-w49st   477m         478Mi           

NAME          REFERENCE                TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
pricing-api   Deployment/pricing-api   cpu: 365%/70%   1         5         4          34m
```

Within 8 seconds, the HPA triggered the maximum scale-up to 5 pods:

```text
Normal   SuccessfulRescale  37s  horizontal-pod-autoscaler  New size: 4; reason: cpu resource utilization (percentage of request) above target
Normal   SuccessfulRescale  29s  horizontal-pod-autoscaler  New size: 5; reason: cpu resource utilization (percentage of request) above target
```

### Pod Rollout List under High Load:
```text
NAME                           READY   STATUS    RESTARTS   AGE
pricing-api-569485c9c4-6g24s   1/1     Running   0          22s
pricing-api-569485c9c4-f9qzs   1/1     Running   0          14s
pricing-api-569485c9c4-l8s4w   1/1     Running   0          22s
pricing-api-569485c9c4-w49st   1/1     Running   0          31m
pricing-api-569485c9c4-wz6nr   1/1     Running   0          22s
```

---

## 4. Workload Identity Verification

From inside the active pod:
```text
$ kubectl exec -n pricing deploy/pricing-api -- python3 -c "import urllib.request; req = urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email', headers={'Metadata-Flavor': 'Google'}); print(urllib.request.urlopen(req).read().decode())"
Active Service Account in Pod via Workload Identity: pricing-app-staging@aditya-devops-lab.iam.gserviceaccount.com
```

Listing models bucket objects via metadata token:
```text
GCS Bucket Objects accessed via Workload Identity: ['pipeline.pkl']
```

---

## 5. Filebeat Logging DaemonSet

```text
NAME                 READY   STATUS    RESTARTS   AGE
pod/filebeat-5xbsb   1/1     Running   0          90s
pod/filebeat-xkjhc   1/1     Running   0          90s
```
- **Forwarding Target:** `10.10.0.3:5044` (`pricing-staging-elk`)
- **Ingested Logs:** Microservice structured JSON logs with `client_ip`, `latency_ms`, and `http_status`.

---

## 6. Conclusion
The Horizontal Pod Autoscaler and GKE Workload Identity behave strictly according to syllabus specifications (Units 7 & 8), successfully dynamically expanding inference capacity under load and securing pod-to-cloud communications.
