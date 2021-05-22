import json
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from bs4 import BeautifulSoup
from mb_commons import FIREFOX_USER_AGENT, Result, hrequest, md


@dataclass
class ParityTrace:
    @dataclass
    class Trace:
        call_type: str
        from_: str
        to: Optional[str]
        gas: int
        value: int
        input: str
        gas_used: int
        output: str

    block_number: int
    transaction_position: int
    traces: list[Trace]


@dataclass
class EtherscanToken:
    erc: str  # erc20 | erc721
    symbol: str
    total_supply: Decimal
    decimals: Optional[int]
    holders_count: int
    transfers_count: int
    price_usd: Optional[Decimal]
    market_cap_usd: Optional[Decimal]
    site: str


@dataclass
class EtherscanInfo:
    name: str
    tags: list[str]
    site: str
    tokens_usd: Decimal
    token: Optional[EtherscanToken]


def get_address_info(address: str, timeout=10, proxy=None) -> Result[EtherscanInfo]:
    url = "https://etherscan.io/address/" + address
    res = hrequest(url, proxy=proxy, user_agent=FIREFOX_USER_AGENT, timeout=timeout)
    if res.is_error():
        return res.to_error()
    if "maximum limit reached for this request" in res.body:
        return res.to_error("request_throttled")
    try:
        soap = BeautifulSoup(res.body, "html.parser")
        if soap.select_one("#mainaddress"):
            name = ""
            tags = []
            site = ""
            tokens_usd = Decimal()

            # name
            name_el = soap.select_one("span[title='Public Name Tag (viewable by anyone)']")
            if name_el:
                name = name_el.text.strip()

            # tags
            for link in soap.select("#content a.u-label"):
                if link.get("href") and link["href"].startswith("/accounts/label/"):
                    tags.append(link["href"].replace("/accounts/label/", ""))

            # token_usd
            tokens_usd_el = soap.select_one("#ContentPlaceHolder1_tokenbalance #availableBalanceDropdown")
            if tokens_usd_el:
                m = re.search(r"\$([\d.,]+)", tokens_usd_el.text)
                if m:
                    value = m.group(1).replace(",", "").replace("...", "").strip()
                    tokens_usd = Decimal(value)

            # site
            site_el = soap.select_one("a[title='External Site - More Info']")
            if site_el:
                site = site_el.get("href", "")

            token = None
            if soap.select_one("a[title='View Token Tracker Page']"):
                token = get_etherscan_token(address, timeout, proxy).ok

            return res.to_ok(EtherscanInfo(**md(name, tags, site, tokens_usd, token)))
        return res.to_error("unknown_response")
    except Exception as e:
        return res.to_error(f"exception: {str(e)}")


def get_token_usd_price(address: str, timeout=10, proxy=None) -> Result[Decimal]:
    url = f"https://etherscan.io/token/{address}"
    res = hrequest(url, proxy=proxy, user_agent=FIREFOX_USER_AGENT, timeout=timeout)
    if res.is_error():
        return res.to_error()
    if "maximum limit reached for this request" in res.body:
        return res.to_error("request_throttled")
    try:
        soap = BeautifulSoup(res.body, "html.parser")
        span = soap.select_one("#ContentPlaceHolder1_tr_valuepertoken span.d-block")
        if span and "@" in span.text:
            return res.to_ok(Decimal(span.text.split("@")[0].strip().replace("$", "")))

        # check if it's a ERC721 token
        span = soap.select_one("#ContentPlaceHolder1_divSummary .card-header-title .text-secondary.small")
        if span and "ERC-721" in span.text:
            return res.to_error("erc721")

        return res.to_error("html_parse_error")
    except Exception as e:
        return res.to_error(f"exception: {str(e)}")


def get_contract_creation_tx_hash(contract_address: str, timeout=10, proxy=None) -> Result[str]:
    url = f"https://etherscan.io/address/{contract_address}"
    res = hrequest(url, timeout=timeout, proxy=proxy, user_agent=FIREFOX_USER_AGENT)
    if res.is_error():
        return res.to_error()
    if "maximum limit reached for this request" in res.body:
        return res.to_error("request_throttled")
    try:
        soap = BeautifulSoup(res.body, "html.parser")
        a = soap.select_one("a.hash-tag[title='Creator Txn Hash']")
        if a and a.text and a.text.startswith("0x"):
            return res.to_ok(a.text)
        else:
            return res.to_error("not_found")
    except Exception as e:
        return res.to_error(f"exception: {str(e)}")


def get_top_accounts(timeout=10, proxy=None) -> Result[list[str]]:
    url = "https://etherscan.io/accounts"
    res = hrequest(url, user_agent=FIREFOX_USER_AGENT, timeout=timeout, proxy=proxy)
    if res.is_error():
        return res.to_error()
    try:
        soap = BeautifulSoup(res.body, "html.parser")
        result = []
        for a in soap.select("#content table td a"):
            link = a.get("href", "")
            if link.startswith("/address/0x"):
                result.append(link.replace("/address/", ""))
        return res.to_ok(result)
    except Exception as e:
        return res.to_error(f"exception: {str(e)}")


def get_top_holders(token_address: str, timeout=10, proxy=None) -> Result[list[str]]:
    url = f"https://etherscan.io/token/generic-tokenholders2?a={token_address}"
    res = hrequest(url, user_agent=FIREFOX_USER_AGENT, timeout=timeout, proxy=proxy)
    if res.is_error():
        return res.to_error()
    if "maximum limit reached for this request" in res.body:
        return res.to_error("request_throttled")
    try:
        soap = BeautifulSoup(res.body, "html.parser")
        result = []
        for a in soap.select("#maintable table td a"):
            m = re.search(r"\?a=(.+)$", a["href"])
            if m:
                result.append(m.group(1))
        if result:
            return res.to_ok(result)
        else:
            div = soap.select_one("#maintable table div.alert-warning")
            if "there are no matching entries" in div.text.lower():
                return res.to_ok([])
            else:
                return res.to_error("html_parse_error")
    except Exception as e:
        return res.to_error(f"exception: {str(e)}")


def get_etherscan_token(address: str, timeout=10, proxy=None) -> Result[EtherscanToken]:
    url = f"https://etherscan.io/token/{address}"
    res = hrequest(url, timeout=timeout, proxy=proxy, user_agent=FIREFOX_USER_AGENT)
    if res.is_error():
        return res.to_error()
    if "maximum limit reached for this request" in res.body:
        return res.to_error("request_throttled")

    try:
        soap = BeautifulSoup(res.body, "html.parser")
        if "[ERC-20]" in res.body:
            erc = "erc20"
        elif "[ERC-721]" in res.body:
            erc = "erc721"
        else:
            erc = "unknown"

        symbol = None
        el = soap.select_one("#ContentPlaceHolder1_hdnSymbol")
        if el:
            symbol = el.get("value")

        total_supply = None
        el = soap.select_one("#ContentPlaceHolder1_hdnTotalSupply")
        if el:
            total_supply = el.get("value")
            if total_supply:
                total_supply = Decimal(total_supply.replace(",", "").strip())

        decimals = None
        el = soap.select_one("#ContentPlaceHolder1_trDecimals")
        if el:
            decimals = el.text
            if decimals:
                decimals = int(decimals.replace("Decimals:", "").strip())

        holders_count = None
        el = soap.select_one("#ContentPlaceHolder1_tr_tokenHolders")
        if el:
            holders_count = el.text
            if holders_count:
                holders_count = int(
                    holders_count.replace("Holders:", "")
                    .replace("addresses", "")
                    .replace("address", "")
                    .replace(",", "")
                    .strip(),
                )

        price_usd = None
        el = soap.select_one("#ContentPlaceHolder1_tr_valuepertoken span.d-block")
        if el and "@" in el.text:
            price_usd = Decimal(el.text.split("@")[0].strip().replace("$", ""))

        market_cap_usd = None
        el = soap.select_one("#pricebutton")

        if el and "$" in el.text:
            market_cap_usd = Decimal(el.text.strip().replace("$", "").replace(",", ""))

        site = None
        el = soap.select_one("#ContentPlaceHolder1_tr_officialsite_1 a")
        if el:
            site = el["href"]

        transfers_count = get_token_transfers_count(address, timeout, proxy).ok

        info = md(erc, symbol, total_supply, decimals, holders_count, transfers_count, price_usd, market_cap_usd, site)
        return res.to_ok(EtherscanToken(**info))
    except Exception as e:
        return res.to_error(f"exception: {str(e)}")


def get_token_transfers_count(address: str, timeout=10, proxy=None) -> Result[int]:
    url = f"https://etherscan.io/token/generic-tokentxns2?m=normal&contractAddress={address}&a="
    res = hrequest(url, timeout=timeout, proxy=proxy, user_agent=FIREFOX_USER_AGENT)
    if res.is_error():
        return res.to_error()
    if "maximum limit reached for this request" in res.body:
        return res.to_error("request_throttled")
    try:
        m = re.search(r"total of ([\d,]+) transaction", res.body)
        if m:
            return res.to_ok(int(m.group(1).replace(",", "")))
        else:
            return res.to_error("unknown_response")
    except Exception as e:
        return res.to_error(f"exception: {str(e)}")


def get_parity_trace(tx_hash: str, timeout=10, proxy=None) -> Result[ParityTrace]:
    url = f"https://etherscan.io/vmtrace?txhash={tx_hash}&type=parity#raw"
    res = hrequest(url, timeout=timeout, proxy=proxy, user_agent=FIREFOX_USER_AGENT)
    if res.is_error():
        return res.to_error()
    if "maximum limit reached for this request" in res.body:
        return res.to_error("request_throttled")
    try:
        soap = BeautifulSoup(res.body, "html.parser")
        editor_el = soap.select_one("#editor")
        if not editor_el:
            return res.to_error("unknown_response")

        traces_json = json.loads(f"[{editor_el.text}]")
        block_number = traces_json[0]["blockNumber"]
        transaction_position = traces_json[0]["transactionPosition"]

        traces: list[ParityTrace.Trace] = []
        for t in traces_json:
            call_type = t["action"]["callType"]
            from_ = t["action"]["from"]
            to = t["action"].get("to")
            gas = int(t["action"]["gas"], 16)
            value = int(t["action"]["value"], 16)
            input_ = t["action"]["input"]
            gas_used = int(t["result"]["gasUsed"], 16)
            output = t["result"]["output"]
            trace = md(call_type, from_, to, gas, value, gas_used, output, input=input_)
            traces.append(ParityTrace.Trace(**trace))
        parity_trace = ParityTrace(block_number=block_number, transaction_position=transaction_position, traces=traces)
        return res.to_ok(parity_trace)
    except Exception as e:
        return res.to_error(f"exception: {str(e)}")
