import requests
import logging

__all__ = ["Document", "DocumentFeed"]

class Document(object):

    def __init__(self, client) -> None:
        super().__init__()
        self.client = client
        self.logger = logging.getLogger(__name__)

    def create(self, data):  # pylint: disable=W8106
        url = self.client.instance_url("/invite")
        data = data or {}
        try:
            self.client.refreshTokenIfRequired()
            response = requests.post(url=url, data=data, headers=self.client.headers(), timeout=15)
            if "ApiErrorCode" in response.headers:
                raise self.client.raise_error("Invite", response)
            json_response = response.json()
            self.logger.debug("Added new mandate : %s" % json_response["mndtId"])
            return json_response
        except requests.exceptions.RequestException as e:
            raise self.client.raise_error_from_request("Invite", e)


    def sign(self, data):  # pylint: disable=W8106
        url = self.client.instance_url("/sign")
        data = data or {}
        try:
            self.client.refreshTokenIfRequired()
            response = requests.post(url=url, data=data, headers=self.client.headers(), timeout=15)
            if "ApiErrorCode" in response.headers:
                raise self.client.raise_error("Sign", response)
            json_response = response.json()
            self.logger.debug("Added new mandate : %s" % json_response["MndtId"])
            return json_response
        except requests.exceptions.RequestException as e:
            raise self.client.raise_error_from_request("Sign", e)

    def update(self, data):
        url = self.client.instance_url("/mandate/update")
        data = data or {}
        try:
            self.client.refreshTokenIfRequired()
            response = requests.post(url=url, data=data, headers=self.client.headers(), timeout=15)
            self.logger.debug("Updated mandate : {} response={}".format(data, response))
            if "ApiErrorCode" in response.headers:
                raise self.client.raise_error("Update", response)
        except requests.exceptions.RequestException as e:
            raise self.client.raise_error_from_request("Update", e)

    def cancel(self, mandate_number, reason):
        url = self.client.instance_url("/mandate?mndtId=" + mandate_number + "&rsn=" + reason)
        try:
            self.client.refreshTokenIfRequired()
            response = requests.delete(url=url, headers=self.client.headers(), timeout=15)
            self.logger.debug("Updated mandate : %s status=%d" % (mandate_number, response.status_code))
            if "ApiErrorCode" in response.headers:
                raise self.client.raise_error("Cancel", response)
        except requests.exceptions.RequestException as e:
            raise self.client.raise_error_from_request("Invite", e)

    def feed(self, documentFeed):
        url = self.client.instance_url("/mandate")
        try:
            self.client.refreshTokenIfRequired()
            headers = self.client.headers()
            headers.update({"X-TYPES": "CORE,B2B,CREDITCARD"})
            response = requests.get(url=url,headers=headers,timeout=15,)
            if "ApiErrorCode" in response.headers:
                raise self.client.raise_error("Feed", response)
            feed_response = response.json()
            while len(feed_response["Messages"]) > 0:
                self.logger.debug("Feed handling : %d from %s" % (len(feed_response["Messages"]), response.headers["X-LAST"]))
                for msg in feed_response["Messages"]:
                    if "AmdmntRsn" in msg:
                        mndt_id_ = msg["OrgnlMndtId"]
                        self.logger.debug("Feed update : %s" % (mndt_id_))
                        mndt_ = msg["Mndt"]
                        rsn_ = msg["AmdmntRsn"]
                        documentFeed.updatedDocument(mndt_id_, mndt_, rsn_)
                    elif "CxlRsn" in msg:
                        self.logger.debug("Feed cancel : %s" % (msg["OrgnlMndtId"]))
                        documentFeed.cancelDocument(msg["OrgnlMndtId"], msg["CxlRsn"])
                    else:
                        self.logger.debug("Feed create : %s" % (msg["Mndt"]))
                        documentFeed.newDocument(msg["Mndt"])
                response = requests.get(url=url,headers=headers,timeout=15,)
                if "ApiErrorCode" in response.headers:
                    raise self.client.raise_error("Feed", response)
                feed_response = response.json()
        except requests.exceptions.RequestException as e:
            raise self.client.raise_error_from_request("Mandate feed", e)

    def update_customer(self, customer_id, data):
        url = self.client.instance_url("/customer/" + str(customer_id))
        try:
            self.client.refreshTokenIfRequired()
            response = requests.patch(url=url, params=data, headers=self.client.headers(), timeout=15)
            if "ApiErrorCode" in response.headers:
                raise self.client.raise_error("Cancel", response)
        except requests.exceptions.RequestException as e:
            raise self.client.raise_error_from_request("Update customer", e)

class DocumentFeed:
    def newDocument(self, doc):
        pass

    def updatedDocument(self, mandate_number, doc, reason):
        pass

    def cancelDocument(self, docNumber, reason):
        pass
