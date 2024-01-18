## Helping UK parents find the best school

Created this repo explore how AI might improve children’s education, by
using our education data and oversight to help parents select the very best school for their
child and explore their options.

Schools are overseen by a range of bodies, such as Ofsted (who produce detailed inspect
reports) and the Department for Education (DfE) who produce statistics and league tables.

This project explores how to help parents select the best
school for their child using data from Ofsted and the DfE. I have built a chatbot that helps parents query
School records on their local schools

## Local Deployment

1. Install dependencies

```bash
pip install -r requirements.txt
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
