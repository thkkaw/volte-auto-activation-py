import json
import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from sqlalchemy import select

from db import SessionLocal
from log_handler import get_logger
from models import OfferCode

load_dotenv()


app = Flask(__name__)


API_URL = os.getenv("API_URL")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "5"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
URL_PREFIX = "/volte-auto-activate"

ENV = os.getenv("ENV", "").strip()
WHITELIST = {
    value.strip() for value in os.getenv("WHITELIST", "").split(",") if value.strip()
}


logger = get_logger(
    worker_id="autovolte",
    level=LOG_LEVEL,
)


def normalize_msisdn(msisdn: str) -> str:

    msisdn = msisdn.strip()

    if msisdn.startswith("95"):
        return msisdn[2:]

    return msisdn


def is_offer_eligible(offer_code: str) -> bool:

    with SessionLocal() as session:

        statement = select(OfferCode.id).where(OfferCode.code == offer_code)

        result = session.execute(statement).scalar_one_or_none()

        return result is not None


def call_volte_api(msisdn: str):

    payload = {
        "msisdn": msisdn,
        "channel": "portal",
    }

    response = requests.post(
        API_URL,
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )

    return response, response.json()


@app.get(URL_PREFIX, strict_slashes=False)
def health():
    return {"status": "ok"}


@app.post(f"{URL_PREFIX}/provision", strict_slashes=False)
def volte_auto_activate():

    try:

        payload = request.get_json(silent=True)

        if not isinstance(payload, dict):

            return (
                jsonify(
                    {
                        "status": "failed",
                        "message": "Invalid JSON payload. Expected an object.",
                    }
                ),
                400,
            )

        msisdn = str(payload.get("MSISDN")).strip()

        offer_code = payload.get("Offer CODE")

        logger.info(
            "Req: %s | %s ",
            msisdn,
            offer_code,
        )

        if ENV == "stg" and normalize_msisdn(msisdn) not in WHITELIST:
            logger.warning(
                "Rejected | %s",
                msisdn,
            )

            return (
                jsonify(
                    {
                        "status": "failed",
                        "message": "SERVICE IS NOT AVAILABLE FOR EXTERNAL",
                    }
                ),
                403,
            )

        #
        # Basic validation
        #
        if not msisdn or not offer_code:

            logger.warning(
                "Invalid transaction: missing msisdn or offer code",
            )

            return (
                jsonify(
                    {
                        "status": "failed",
                        "message": "MSISDN and Offer CODE are required.",
                    }
                ),
                400,
            )

        #
        # Eligibility check
        #
        eligible = is_offer_eligible(offer_code)

        #
        # Not eligible
        #
        if not eligible:

            logger.info(
                "not eligible, %s | %s ",
                msisdn,
                offer_code,
            )

            return jsonify({"status": "not eligible"}), 200
        

        volte_msisdn = normalize_msisdn(msisdn)

        logger.info(
            "eligible, %s | %s ",
            msisdn,
            offer_code,
        )

        try:

            response, response_data = call_volte_api(volte_msisdn)

            #
            # Mr.P success
            #
            if 200 <= response.status_code < 300:

                logger.info(
                    "VoLTE Sub API success | %s | %s",
                    response.status_code,
                    json.dumps(response_data, ensure_ascii=False, default=str),
                )

                return jsonify({"status": "success"}), 200

            #
            # Mr.P returned 4xx / 5xx
            #
            logger.info(
                "VoLTE Sub API failed | %s | %s",
                response.status_code,
                json.dumps(response_data, ensure_ascii=False, default=str),
            )

            return jsonify({"status": "failed"}), 500

        except requests.RequestException:

            logger.exception("VoLTE api request failed")

            return (
                jsonify(
                    {
                        "status": "failed",
                        "message": "Unable to communicate with VoLTE endpoint.",
                    }
                ),
                500,
            )

    except Exception:

        logger.exception("Activation failed unexpectedly")

        return (
            jsonify({"status": "failed", "message": "An unexpected error occurred."}),
            500,
        )


if __name__ == "__main__":
    app.run()
