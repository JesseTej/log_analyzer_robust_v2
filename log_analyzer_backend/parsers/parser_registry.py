from .auth_parser import AuthParser
from .nginx_parser import NginxParser  

PARSERS = {
    "auth": AuthParser,
    "nginx": NginxParser,
}
