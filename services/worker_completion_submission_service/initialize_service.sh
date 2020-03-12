# Run this from the root of cloud runner

cp -r queuingservices services/worker_completion_submission_service/queuingservices
cp -r servicecommon services/worker_completion_submission_service/servicecommon
cp -r storage services/worker_completion_submission_service/storage
cp -r worker services/worker_completion_submission_service/worker
cp shellscripts/shared/pip_fail_safe_install.sh services/worker_completion_submission_service/pip_fail_safe_install.sh
cp requirements.txt services/worker_completion_submission_service/requirements.txt

cd services/worker_completion_submission_service || exit

docker-compose up --build

rm -r queuingservices
rm -r servicecommon
rm -r storage
rm -r worker

rm requirements.txt
rm pip_fail_safe_install.sh


