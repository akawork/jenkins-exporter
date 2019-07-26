import argparse
import ast
import os
import sys
import configparser

config = configparser.ConfigParser()
config.read(os.environ.get('JENKINS_CONFIG_FILE'))

def parse_args():
    
    parser = argparse.ArgumentParser(
        description='jenkins exporter'
    )
    parser.add_argument(
        '-s', '--server',
        metavar='server',
        required=False,
        help='server url from the jenkins api',
        default=config['DEFAULT']['JENKINS_SERVER']
    )
    parser.add_argument(
        '--user',
        metavar='user',
        required=False,
        help='jenkins api user',
        default=config['DEFAULT']['JENKINS_USERNAME']
    )
    parser.add_argument(
        '--passwd',
        metavar='passwd',
        required=False,
        help='jenkins api password',
        default=config['DEFAULT']['JENKINS_PASWORD']
    )
    parser.add_argument(
        '-p', '--port',
        metavar='port',
        required=False,
        type=int,
        help='Listen to this port',
        default=int(config['DEFAULT']['VIRTUAL_PORT'])
    )
    parser.add_argument(
        '-k', '--insecure',
        dest='insecure',
        required=False,
        action='store_true',
        help='Allow connection to insecure Jenkins API',
        default=False
    )
    return parser.parse_args()