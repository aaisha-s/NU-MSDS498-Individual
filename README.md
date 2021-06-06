## NU-MSDS498-Individual

Using AWS Lambda, S3, CloudWatch, DynamoDB, and Comprehend I was able to do a mass Sentiment Analysis on a batch of 400 consumer reviews saved in one .csv file

1. Sign up for AWS accounts
2. Create a LambdaAccount in IAM with full access to S3, Comprehend, DynamoDB, and CloudWatch
3. Create a trigger Lambda (code included) to pull new imports into the S3 bucket, perform sentiment Analysis, and save data to DynamoDB

```

import json
import boto3
import uuid

#base setup
s3_client = boto3.client("s3")
comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb')
cust_reviews_table = dynamodb.Table('cust-reviews')

def lambda_handler(event, context):
	#pull in a csv file and parse
	source_bucket_name = event['Records'][0]['s3']['bucket']['name']
	file_name = event['Records'][0]['s3']['object']['key']

	file_object = s3_client.get_object(Bucket = source_bucket_name, Key = file_name)
	print("file_object : ", file_object)

	file_content = file_object['Body'].read().decode("utf-8")
	print("file_content : ", file_content)

	#parse through each row of the csv. 
	fullReviews = file_content.split("\n")
	print("review data : ", fullReviews)
	
	#within in each row, breakup the columns with a ',' delimiter
	for eachReview in fullReviews:
		reviewRow = eachReview.split(",")
		#based on my sheet, the actual text of the review is in the [2] slot
		reviewText = reviewRow[2]
		#this code performs the actual sentiment analysis. You can have an option of Positive
		#Negative, or Mixed for sentiment. This also saves the score of confidence rating
		comp_sentiment = comprehend.detect_sentiment(Text=reviewText, LanguageCode='en')
		sentiment = comp_sentiment['Sentiment']
		score =  str(comp_sentiment['SentimentScore'][comp_sentiment['Sentiment'].title()])
		
		#Lastly, push all the data from the s3 csv file into a DynamoDB
		cust_reviews_table.put_item(
			Item = {
				'guid' : str(uuid.uuid4()),
				'Clothing_ID' : reviewRow[0],
				'Age' : reviewRow[1],
				'ReviewText' : reviewRow[2][:10000],
				'Rating' : reviewRow[3],
				'ItemName' : reviewRow[4],
				'Sentiment' : sentiment,
				'SentimentScore' :  score
			}
			)
```
