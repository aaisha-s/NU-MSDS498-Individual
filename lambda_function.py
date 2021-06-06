
import json
import boto3
import uuid

s3_client = boto3.client("s3")
comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb')
cust_reviews_table = dynamodb.Table('cust-reviews')

def lambda_handler(event, context):
	source_bucket_name = event['Records'][0]['s3']['bucket']['name']
	file_name = event['Records'][0]['s3']['object']['key']

	file_object = s3_client.get_object(Bucket = source_bucket_name, Key = file_name)
	print("file_object : ", file_object)

	file_content = file_object['Body'].read().decode("utf-8")
	print("file_content : ", file_content)

	fullReviews = file_content.split("\n")
	print("review data : ", fullReviews)
	
	for eachReview in fullReviews:
		reviewRow = eachReview.split(",")
		reviewText = reviewRow[2]
		comp_sentiment = comprehend.detect_sentiment(Text=reviewText, LanguageCode='en')
		sentiment = comp_sentiment['Sentiment']
		score =  str(comp_sentiment['SentimentScore'][comp_sentiment['Sentiment'].title()])
		
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
