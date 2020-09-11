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

	# parse parallelism
	print("Initialize parallel codes")
	depressed_queue = multiprocessing.Queue()
	nondepressed_queue = multiprocessing.Queue()
	depressed_process = [Process(target = extract_comments, args = (reddit, id, depressed_queue)) for id in depressed.keys()]
	nondepressed_process = [Process(target = extract_comments, args = (reddit, id, nondepressed_queue)) for id in nondepressed.keys()]

	# execute parallelism
	print("Execute code parallelism")
	# run processes
	for d, n in zip(depressed_process, nondepressed_process):
		d.start()
		n.start()

	# exit processes
	for d, n in zip(depressed_process, nondepressed_process):
		d.join()
		n.join()

	# get text
	pritn("Get depression and nondepression comments")
	depressed_comemnts = {}
	for process, id in zip(depressed_process, depressed.keys()):
		depressed_comemnts[id] = depressed_queue.get()

	nondepressed_comemnts = {}
	for process, id in zip(nondepressed_process, nondepressed.keys()):
		nondepressed_comemnts[id] = nondepressed_queue.get()

	# save data
	# save sub-topics
	print("Write depression and nondepression topics")
	with open('depressed_topics.json', 'w') as file:
		json.dumps(file)
	with open('nondepressed_topics.json', 'w') as file:
		json.dumps(file)

	# save comments
	print("Write depression and nondepression comments")
	with open('depressed_comments.json', 'w') as file:
		json.dumps(file)
	with open('nondepressed_comemnts.json', 'w') as file:
		json.dumps(file)

def extract_comments(reddit, id, output):
	print("Get comments for id - {}".format(id))
	results = []
	for comment in  reddit.submission(id = id).comments:
		if not isinstance(comment, MoreComments):
			# add main comment
			results.append(comment.body)
		else:
			# add children
			for child in comment.children:
				results.extend(reddit.submission(id = child).comments.list())
	#print(results)
	#input()
	output.put(results)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = 'Argument Parser')
	parser.add_argument('--credentials', type=str, default = 'credentials.json')
	main(parser.parse_args())
