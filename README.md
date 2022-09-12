# Zoomcamp Projects Lambda

API for generating github repositories for Zoomcamp projects


### Environment variables

Copy `.envrc_template` to `.envrc` and replace TODOs with the actual 
keys

Use `direnv` or `$(cat .envrc)` for populating the env variables

### Lambda

Function name: `automator-zoomcamp-projects`

To publish a new version, use

```
make publish
```

To copy the env variables from local env to lambda, use 

```
make update_env
```

### API Gateway 

* Type: HTTP API
* Route: `ANY /{thepath+}`
* Integration: lambda


### SQS

* We use the queue for projects available for students
* We pre-register github repos, populate the queue when invoked, the students get a ready-to-use repo
* Queue name: `zoomcamp-projects`

<details>
<summary>Policy for the lambda function (example):</summary>  

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup"
            ],
            "Resource": [
                "arn:aws:logs:eu-west-1:387546586013:*"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:eu-west-1:387546586013:log-group:/aws/lambda/automator-zoomcamp-projects:*"
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": [
                "sqs:DeleteMessage",
                "sqs:ReceiveMessage",
                "sqs:SendMessage",
                "sqs:CreateQueue"
            ],
            "Resource": [
                "arn:aws:sqs:eu-west-1:387546586013:zoomcamp-projects"
            ]
        }
    ]
}
```
</details>



### DynamoDB 

We want to know if a student has already been assigned a project 
