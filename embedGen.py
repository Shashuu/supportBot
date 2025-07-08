from flask import Flask, request
from http import HTTPStatus

from service.embedding.embedGenService import EmbedGen

from utils.commonUtil import getConfig
from utils.logger import Logger
from utils.responseUtil import build_response

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--conf")
parser.add_argument("--port")
args = parser.parse_args()

conf = getConfig(args.conf)

log = Logger(conf["logpath"])
embedService = EmbedGen(model = conf["model"])

app = Flask(__name__)

@app.route("/healthcheck", methods=["POST"])
def ping():
    return build_response(HTTPStatus.OK, {"ping": "pong"})

@app.route("/get-embedding", methods=["POST"])
def get_embedding():
    try:
        req = request.json
        data = req["data"]
        embed = embedService.getEmbed(data)
        return build_response(HTTPStatus.OK, {"embedding": embed.tolist()})
    except Exception as e:
        log.exception(f"failed to process with reason {str(e)}")
        return build_response(HTTPStatus.INTERNAL_SERVER_ERROR, dict())

if __name__ == '__main__':
    app.run(host=conf["host"], port=int(args.port))