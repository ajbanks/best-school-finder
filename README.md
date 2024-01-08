

## Local Deployment

1. Install dependencies

```bash
pip install -r requirements/requirements.txt
```

2. Run the application

```bash
python app.py
```

## Deploying to AWS Lambda

1. install the AWS CDK CLI

```bash
npm install -g aws-cdk
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Bootstrap the CDK

_[optional]: export aws profile_
```
export AWS_PROFILE=hf-sm
```

Boostrap project in the cloud
```
cdk bootstrap
```

4. Deploy Gradio application to AWS Lambda

```bash
cdk deploy 
```

1. Delete AWS Lambda again

```bash
cdk destroy
```
