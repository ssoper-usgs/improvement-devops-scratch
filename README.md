# improvement-devops-scratch

This exercise will present you with application code and an ongoing operational issue.
You will be provided with a brief background regarding the purpose of the application,
some details regarding the operational issues, and then questions for you to consider.
You need not answer all the questions nor be constrained by them--the goal of this
exercise for you to get a sense of the domain and for us to understand how you think 
and problem-solve.

## Background

This repo contains two AWS Lambda functions intended to help with QA/QC of data coming
from a UV-Vis spectrophotometer. Data from the spectrophotometer lands in an SQS queue and
subsequently triggers the data check Lambda function. If a data issue is
identified, another Lambda is triggered to send a notification to lab staff.

## Operational Observations

Here are some observations that a developer has noticed regarding the system:

* Runtimes for both Lambdas are about 200 ms. 
* The quality check Lambda reports using 108 MB of memory on average.
* The notification Lambda reports using 90 MB on memory of average.
* The quality check Lambda works 99.9 % of the time.
* The notification Lambda fails 10 % of the time. No one is notified after the 
failure, and there's no record of the erroneous data.
* It is difficult to figure out which sample's data might have caused a failure.


## Prompts

Please submit you exercise responses to eread@usgs.gov either in the body of an email or in an attachment. Each 
question maybe addressed with a few sentences or a short paragraph.

Questions to consider:

1. What is the purpose of the serverless.yml file?
   1. The serverless.yml file is a config file used to define assets being deployed to the cloud (aws in this case).
2. What is the purpose of the pyproject.toml file?
   1. The .toml file is the config figle used by the poetry dependency management tool.  Sort of like combining Python's 
    built-in pip (with its requirements.txt file) and virtualenv into one easy-to-use tool. It also contains other project 
    information as part of the config so you can view top level dependency/project information at a glance.
3. What other pieces of information would you want to see to help investigate the operational issues? 
How might that information be acquired?
   1. Generally, it would be good to see an cloudwatch dashboard that monitored all the assets in the serverless stack side-by-side
     to get a sense of overall performance over time.  We could also just leverage the aws UI lambda pages to see performance
     over time as well.  This information would help determine when the error started, how long it's been happening, etc. so that 
     a troubleshooter could figure out if the error was due to a code change that was deployed along the same time interval. Once a fix
      is in place, this same information can be used to see if the error rate is dropping or is eliminated.
4. What are your thoughts on code quality and tests within the repo? What tools and techniques could be used to improve it?
   1. The existing code and tests seem fine.
   2. However, without a coverage tool, it's hard to know exactly which lines/branches of code are covered.
   3. Locally, you could add coverage or pytest-cov to get a better picture of coverage metrics and address any weak points.
   4. I don't see a CI/CD tool as part of the codebase, but if this code were to be deployed I would want to see a 
   build/deploy tool like travis-CI, code quality tools like codacy, and code coverage tools included so that unit tests/coverage/quality
   metrics were displayed on merge requests as part of a peer review process to ensure very high levels of code quality.
5. Are there improvements that you would make to the application code to address the operational issues?
   1. I want to see an error stack trace when the failure happens, along with metadata about the failed record. 
    This can be achieved by logging the exception in the except block of the `data_quality_check_handler` method in the 
    `handler.py` module.  I would also raise an error there instead of passing, so that the lambda fails when the notification
    fails, making it more clear to a dev/ops person that something is wrong.
   2. From there we could figure out why the notification fails to send and iterate to make it more reliable.
   3. Also the `awslambda.py` module's invoke method returns the lambda invocation response, but the response is not 
     interpreted for success or failure anywhere. It would be helpful to raise an exception if the lambda response came
     back as anything other than successful.
6. Are there improvements that you would make to the infrastructure-as-code to address the operational issues?
   1. I would add an sqs queue asset that the `data_quality_check_handler` would populate with events (failed qc checks).
      1. As part of that, I would rename the `awslambda.py` module to something like `awsSqs.py` and use it to populate
         an sqs queue instead of invoking a lambda.
      2. I would add an event trigger for this new queue to the existing `problemNotifier` lambda so that it triggered off
         of these events, rather than being triggered via direct lambda invocation in the code via the other lambda, `data_quality_check_handler`.
      3. Coupled with better exception handling, re-organizing the code this way would make it easier to figure out which 
         lambda is failing.
7. Are there optimizations within the infrastructure-as-code that could potentially reduce operational costs?
   1. The developer mentions that each lambda uses between 90 and 108mb of memory, but in the configuration these assets are 
      each configured to use 512mb.  This might be adding extra cost to these invocations. To reduce costs, one could lower
      the provisioned memory to someting like 256 or 128mb. If there is not a significant performance hit, that should save some money.
      Then again, the extra memory might be making the lambdas so fast that the cost is made up in lower invocation times. Typically some
      experimentation is best to determine the best value here.
8. Are there different tools and/or different ways of putting things together that would be more effective?
   1. Addressed in 6 above.
   2. Separating the lambdas by a queue would also offer better scaling opportunities.  That way if one lambda sees 
      a lot more use than the other (probably the qc lambda in this case, assuming failures are less common) - it could 
      have much higher concurrency values and its batch size could be increased.  The events it placed in the sqs queue 
      based on my proposed changes would allow you to individually provision the notifier lambda in a similar way to 
      fully optimize each lambda's performance, without one lambda's p
9. Are there any other improvements that you can think of?
   1. Not 

## Running the unit tests:
```shell
# only works off vpn
poetry shell
poetry install
pytest

# beyond this, I don't think we have coverage tools at the ready here, but would be good to add them.  Something like
# coverage would be fine, or since we have pytest already, pytest-cov would also be fine.
```
