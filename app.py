import hashlib

from datetime import datetime
from flask import Flask, request

import pandas as pd
from feedgen.feed import FeedGenerator
from urllib.parse import urlparse
import re

app = Flask(__name__)

submissions = pd.DataFrame(columns=[
    'id', 'title', 'author', 'text', 'url',
    'created_at', 'title_md5', 'text_md5',
    'title_len_ch', 'text_len_ch',
    'title_len_words', 'text_len_words',
    'url_hostname', 'url_scheme', 'submitted_by'
])

# Set "title" and "author" columns as indexes
submissions.set_index(['title', 'author'], inplace=True)


# Function to generate a unique submission ID
def generate_submission_id():
    return hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()


# Function to calculate the MD5 hash of a string
def calculate_md5_hash(data):
    return hashlib.md5(data.encode()).hexdigest()

# Function to fetch scheme from URL
def fetch_scheme(url):
    url_to_parse = urlparse(url)
    return url_to_parse.scheme


# Function to fetch hostname from URL
def fetch_hostname(url):
    url_to_parse = urlparse(url)
    return url_to_parse.hostname

@app.route('/submit', methods=['POST'])
def submit():
    # TODO: implement sanitization and validation here: not needed for the prototype
    # use marshmellow for future iterations

    # Accept JSON submission from the generator and add additional fields
    submission = request.get_json()
    submission_id = generate_submission_id()
    created_at = datetime.now().astimezone().isoformat()
    title_md5 = calculate_md5_hash(submission['title'])
    text_md5 = calculate_md5_hash(submission['text'])
    title_len_ch = len(submission['title'])
    text_len_ch = len(submission['text'])
    title_len_words = len(submission['title'].split())
    text_len_words = len(submission['text'].split())
    url_hostname = fetch_hostname(submission['url'])
    url_scheme = fetch_scheme(submission['url'])
    submitted_by = request.headers.get('User-Agent')

    entry = {
        'id': [submission_id],
        'title': [submission['title']],
        'author': [submission['author']],
        'text': [submission['text']],
        'url': [submission['url']],
        'created_at': [created_at],
        'title_md5': [title_md5],
        'text_md5': [text_md5],
        'title_len_ch': [title_len_ch],
        'text_len_ch': [text_len_ch],
        'title_len_words': [title_len_words],
        'text_len_words': [text_len_words],
        'url_hostname': [url_hostname],
        'url_scheme': [url_scheme],
        'submitted_by': [submitted_by]
    }

    new_entry = pd.DataFrame(entry)
    new_entry.set_index(['title', 'author'], inplace=True)

    global submissions
    submissions = pd.concat([submissions, new_entry])

    return f"{submission_id} created", 201


@app.route('/search', methods=['GET'])
def search():
    # Search over submitted data and return JSON result
    title_query = request.args.get('title', '')
    author_query = request.args.get('author', '')
    if request.args.get('size'):
        size_limit = int(request.args.get('size'))
    else:
        size_limit = 50

    filtered_submissions = submissions.copy()
    if title_query:
        filtered_submissions = filtered_submissions[
            filtered_submissions.index.get_level_values('title').str.contains(re.escape(title_query), case=False)
        ]
    if author_query:
        filtered_submissions = filtered_submissions[
            filtered_submissions.index.get_level_values('author').str.lower() == author_query.lower()
            ]

    # sort on filtered data before returning
    filtered_submissions.sort_values(by='created_at', inplace=True, ascending=False)

    return filtered_submissions.reset_index(inplace=False).head(size_limit).loc[:,
           ['id', 'title', 'author', 'text', 'created_at']].to_json(orient='records'), 200


@app.route('/item/<submission_id>', methods=['GET'])
def get_item(submission_id):
    # Return specific submission with all fields in JSON format
    submission = submissions[submissions['id'] == submission_id]
    if not submission.empty:
        return submission.reset_index(inplace=False).to_json(orient='records'), 200

    return 'Submission not found', 404


@app.route('/rss', methods=['GET'])
def get_rss():
    title_query = request.args.get('title', '')
    author_query = request.args.get('author', '')
    if request.args.get('size'):
        size_limit = int(request.args.get('size'))
    else:
        size_limit = 50

    filtered_submissions = submissions.copy()
    if title_query:
        filtered_submissions = filtered_submissions[
            filtered_submissions.index.get_level_values('title').str.contains(re.escape(title_query), case=False)
        ]
    if author_query:
        filtered_submissions = filtered_submissions[
            filtered_submissions.index.get_level_values('author').str.lower() == author_query.lower()
            ]

    fg = FeedGenerator()
    fg.title('Submissions RSS Feed')
    fg.link(href=f"{request.host_url}rss")
    fg.description('RSS feed for submissions')

    filtered_submissions.sort_values(by='created_at')
    filtered_submissions.reset_index(inplace=True)
    for _, submission in filtered_submissions.iterrows():
        fe = fg.add_entry()
        fe.guid(f"{request.host_url}item/{submission['id']}")
        fe.title(submission['title'])
        fe.source(submission['author'])
        fe.link(href=submission['url'])
        fe.pubDate(submission['created_at'])

        if len(fg.entry()) == size_limit:
            break

    rss_feed = fg.rss_str(pretty=True)

    return rss_feed, 200
