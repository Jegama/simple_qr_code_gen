@REM # build docker image
docker build -t jmancilla-toolkit .

@REM # tag docker image
docker tag jmancilla-toolkit us-west1-docker.pkg.dev/mypersonalassistant-woypcg/jmancilla-toolkit/jmancilla-toolkit

@REM # create repository
@REM gcloud artifacts repositories create streamlit-parrot --repository-format=docker --location=us-west1 --description="streamlit-parrot"

@REM # push docker image
docker push us-west1-docker.pkg.dev/mypersonalassistant-woypcg/jmancilla-toolkit/jmancilla-toolkit

@REM # deploy docker image to cloud run
gcloud run deploy jmancilla-toolkit --project mypersonalassistant-woypcg --image us-west1-docker.pkg.dev/mypersonalassistant-woypcg/jmancilla-toolkit/jmancilla-toolkit --region us-west1 --platform managed --allow-unauthenticated --port 80 --memory 512Mi --cpu 1 --timeout 300 --max-instances 4 --min-instances 1