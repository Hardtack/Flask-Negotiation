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
            pdict[name] = value
    return key, pdict


def _parse_header_params(s):
    li = []
    while s[:1] == ';':
        s = s[1:]
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
        if isinstance(other, basestring):
            return unicode(self) == other
        return (self.main_type == other.main_type and
                self.sub_type == other.sub_type)

    def __repr__(self):
        return '<media type:' + str(self) + '>'

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u'; '.join([u'%s/%s' % (self.main_type, self.sub_type)] +
                          [u'%s=%s' % (k, v)
                           for k, v in self.params.iteritems()])

    def __cmp__(self, other):
        return cmp(float(self.quality),
                   float(other.quality))

    @property
    def quality(self):
        q = self.params.get('q', None)
        if q is None:
            return 1.0
        return float(q)


def acceptable_media_types(request):
    """Extract acceptable media types from request
    """
    if 'accept' in request.headers:
        li = [x.strip() for x in request.headers['accept'].split(',')]
    else:
        li = ['*/*']
    li = li or ['*/*']
    return sorted(map(MediaType, li), reverse=True)


def best_renderer(renderers, media_types):
    """Choose best renderer and media type
    """
    choosen_items = []
    for media_type in media_types:
        for renderer in renderers:
            choosen = renderer.choose_media_type(media_type)
            if not choosen is None:
                choosen_items.append((renderer, choosen, media_type))
    if not choosen_items:
        return None, None

    def cmp_types(first, second):
        renderer1, choosen1, media_type1 = first
        renderer2, choosen2, media_type2 = second
        if media_type1.quality == media_type2.quality:
            if media_type1 in media_types and media_type2 in media_types:
                cmp(media_types.index(media_type2),
                    media_types.index(media_type1))
            elif media_type1 in media_types:
                return media_type1
            elif media_type2 in media_types:
                return media_type2
            else:
                cmp(renderers.index(renderer1), renderers.index(renderer2))
        return cmp(media_type1.quality, media_type2.quality)

    return tuple(sorted(choosen_items, cmp=cmp_types)[-1][:2])


def choose_media_type(acceptables, media_types):
    """Choose best acceptable media type.
    :param acceptables: list of media type acceptable
    :param media_types: list of media type supported

    :returns: best acceptable media type or :const:`None` if cannot handle.
    """
    choosen = []
    for acceptable in acceptables:
        for media_type in media_types:
            if acceptable in media_type:
                choosen.append((acceptable, media_type))
    if not choosen:
        return None

    def cmp_types(first, second):
        acceptable1, media_type1 = first
        acceptable2, media_type2 = second
        if acceptable.quality == acceptable2.quality:
            return cmp(acceptables.index(acceptable2),
                       acceptables.index(acceptable1))
        return cmp(acceptable.quality, acceptable.quality)

    return sorted(choosen, cmp=cmp_types)[-1][0]


def can_accept(acceptables, media_types):
    """Determines acceptablility.
    :param acceptables: list of media type acceptable
    :param media_types: list of media type supported

    """
    return choose_media_type(acceptables, media_types) is not None
