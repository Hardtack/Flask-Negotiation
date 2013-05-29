""":mod:`media_type`
====================

HTTP media type
"""

def parse_header(s):
    """Parses parameter header
    """
    params = _parse_header_params(';'+s)
    key = params.pop(0).lower()
    pdict = {}
    for param in params:
        i = param.find('=')
        if i >= 0:
            name = param[:i].strip().lower()
            value = param[i+1:].strip()
            if len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1]
                value = value.replace(r'\\', '\\').replace(r'\"', '"')
            pdict[name]=value
    return key, pdict

def _parse_header_params(s):
    li = []
    while s[:1] == ';':
        s=s[1:]
        end = s.find(';')
        while end > 0 and s.count('"', 0, end) % 2:
            # For quote
            end = s.find(';', end+1)
        end = end if end >= 0 else len(s)
        li.append(s[:end].strip())
        s = s[end:]
    return li

class MediaType(object):
    """Abstracted media type class.  
    """
    def __init__(self, raw):
        raw = raw or ''
        self.raw = raw
        self.media_type, self.params = parse_header(raw)
        self.main_type, sep, self.sub_type = self.media_type.partition('/')

    def __contains__(self, other):
        for k, v in self.params.iteritems():
            if k != 'q' and other.params.get(k, None) != v:
                return False
        if self.main_type == '*' and self.sub_type == '*':
            return True
        if self.sub_type == '*' and self.main_type == other.main_type:
            return True
        if self.main_type == '*' and self.sub_type == other.sub_type:
            return True
        return self == other

    def __eq__(self, other):
        return (self.main_type == other.main_type and self.sub_type ==
            other.sub_type)

    def __repr__(self):
        return '<media type:' + str(self) + '>'

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u'; '.join(
            [u'%s/%s' % (self.main_type, self.sub_type)] +
            [u'%s=%s' % (k, v) for k, v in self.params.iteritems()]
        )

    def __cmp__(self, other):
        return cmp(
            float(self.params.get('q', '1.0')),
            float(other.params.get('q','1.0'))
        )

def acceptable_media_types(request):
    """Extract acceptable media types from request
    """
    if request.headers.has_key('accept'):
        li = [
            x.strip() for x in request.headers['accept'].split(',')
        ]
    else:
        li =  ['*/*']
    li = li or ['*/*']
    return sorted(map(MediaType, li), reverse=True)

def best_renderer(renderers, media_types):
    """Choose best renderer and media type
    """
    for media_type in media_types:
        for renderer in renderers:
            if renderer.can_render(media_type):
                return renderer, renderer.choose_media_type(media_type)
    return None, None

def can_accept(acceptables, media_types):
    """Determines acceptablility.  
    :param media_types: list of media type supported
    :param acceptables: list of media type acceptable
    """
    for acceptable in acceptables:
        for media_type in media_types:
            if acceptable in media_type:
                return True
    return False
