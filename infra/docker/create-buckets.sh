#!/bin/sh
# Wait for MinIO to start
/usr/bin/mc alias set myminio http://minio:9000 minioadmin minioadmin
/usr/bin/mc mb myminio/steadyvox-audio || true
/usr/bin/mc anonymous set download myminio/steadyvox-audio || true
exit 0
