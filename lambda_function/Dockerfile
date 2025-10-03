# Use AWS Lambda Python 3.12 base image
# IMPORTANT: Use linux/amd64 platform for compatibility

FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.12

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements and install dependencies
COPY lambda_function/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire rag_core package (reusable core logic)
COPY rag_core/ ${LAMBDA_TASK_ROOT}/rag_core/

# Copy Lambda handler
COPY lambda_function/app.py ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD ["app.lambda_handler"]