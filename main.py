"""
main.py - module to implement Python Reddit API Wrapper to crawl text data of depression and relevant topics
"""

# import dependencies
import argparse
import os
import json
import praw
from praw.models import MoreComments
import multiprocessing
from multiprocessing import Process, Pool

def main(args):
	"""
	main - function to crawl text data of depression and relevant topics
	"""
	# laod credentials
	with open(args.credentials, 'r') as file:
		credentials = json.load(file)

	# create reddit instance
	reddit = praw.Reddit(client_id = credentials['client_id'],
		client_secret = credentials['client_secret'],
		username =  credentials['username'],
		password = credentials['password'],
		user_agent = credentials['user_agent'])

	# get topic and comments under /r/depression
	print("Get depression topics")
	depressed = {}
	for submission in reddit.subreddit('depression').hot():
		depressed[submission.id] = {
			'title' : submission.title,
			'score' : submission.score,
			'url' : submission.url}

	for submission in reddit.subreddit('depression').top():
		depressed[submission.id] = {
			'title' : submission.title,
			'score' : submission.score,
			'url' : submission.url}
	for submission in reddit.subreddit('depression').new():
		depressed[submission.id] = {
			'title' : submission.title,
			'score' : submission.score,
			'url' : submission.url}

	# get topic and comments under /r/AskReddit
	print("Get nondepression topics")
	nondepressed = {}
	for submission in reddit.subreddit('AskReddit').hot():
		nondepressed[submission.id] = {
			'title' : submission.title,
			'score' : submission.score,
			'url' : submission.url}
	for submission in reddit.subreddit('AskReddit').top():
		nondepressed[submission.id] = {
			'title' : submission.title,
			'score' : submission.score,
			'url' : submission.url}
	for submission in reddit.subreddit('AskReddit').new():
		nondepressed[submission.id] = {
			'title' : submission.title,
			'score' : submission.score,
			'url' : submission.url}

	pools = Pool(processes = 10)
	depressed_processes = []
	nondepressed_processes = []
	for id in depressed.keys():
		#try:
			depressed_processes.append(pools.apply_async(extract_comments, args = (reddit, id)))
		#except:
		#	continue
	for id in nondepressed.keys():
		#try:
			nondepressed_processes.append(pools.apply_async(extract_comments, args = (reddit, id)))
		#except:
		#	continue

	# execute parallelism
	depressed_counts = 0
	nondepressed_counts = 0
	print("Execute code parallelism: Getting comments")
	depressed_comments = {}
	for process, id in zip(depressed_processes, depressed.keys()):
		comments, count = process.get()
		depressed_comments[id] = comments
		depressed_counts += count
	nondepressed_comments = {}
	for process, id in zip(nondepressed_processes, nondepressed.keys()):
		comments, count = process.get()
		nondepressed_comments[id] = comments
		nondepressed_counts += count
	# save data
	# save sub-topics
	print("Write depression and nondepression topics")
	with open('depressed_topics.json', 'w') as file:
		json.dump(depressed, file)
	with open('nondepressed_topics.json', 'w') as file:
		json.dump(nondepressed, file)

	# save comments
	print("Write depression and nondepression comments")
	with open('depressed_comments.json', 'w') as file:
		json.dump(depressed_comments, file)
	with open('nondepressed_comemnts.json', 'w') as file:
		json.dump(nondepressed_comments, file)
	print("Depressed Counts", depressed_counts)
	print("Nondepressed Counts", nondepressed_counts)

def extract_comments(reddit, id):
	print("Get comments for id - {}".format(id))
	results = []
	count = 0
	submission = reddit.submission(id = id)
	for _ in range(5):
		try:
			submission.comments.replace_more(limit = 20)
			break
		except:
			print("Continue -", id)
	print("Skip")
	for comment in submission.comments.list():
		if not isinstance(comment, MoreComments):
			results.append(comment.body)
			count += 1
	print("Count of comments", count)
	return results, count

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = 'Argument Parser')
	parser.add_argument('--credentials', type=str, default = 'credentials.json')
	main(parser.parse_args())
