
FUNCTION_NAME="automator-zoomcamp-projects"
BUILD_PATH=`cygpath -w ${PWD}`/build.zip

aws lambda update-function-code \
    --function-name ${FUNCTION_NAME} \
    --zip-file fileb://${BUILD_PATH}