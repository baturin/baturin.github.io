from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
import os
import re
import json
from . import settings
from . import utils
from . import languages
from . import models
from django.db.models import Q


class WikivoyageListingsFile(object):
    def __init__(self, name, language, date, file_format, is_compressed):
        self._name = name
        self._language = language
        self._date = date
        self._file_format = file_format
        self._is_compressed = is_compressed

    @staticmethod
    def parse(filename):
        m = re.match('^wikivoyage-listings-(\S{2})-([^.]+).(.*?)(.bz2|)$', filename)
        if not m:
            return None
        else:
            return WikivoyageListingsFile(
                filename, m.group(1), m.group(2), m.group(3), m.group(4) == '.bz2'
            )

    @property
    def language_code(self):
        return self._language

    @property
    def language_title(self):
        return {
            'en': 'English',
            'ru': 'Russian',
            'fr': 'French',
            'de': 'German',
        }.get(self.language_code, 'Unknown')

    @property
    def date_title(self):
        if self.is_latest:
            return 'Latest'
        else:
            return self._date

    @property
    def file_format(self):
        return self._file_format

    @property
    def file_format_title(self):
        return {
            'csv': 'CSV',
            'kml': 'KML',
            'gpx': 'GPX',
            'sql': 'SQL',
            'osmand.gpx': 'GPX for OsmAnd',
            'obf': 'OBF (for OsmAnd), "wikivoyage" POI type',
            'user-defined.obf': 'OBF (for OsmAnd), "user-defined" POI type',
            'generic.xml': 'XML',
            'xml': 'OsmAnd XML, "wikivoyage" POI type',
            'user-defined.xml': 'OsmAnd XML, "user-defined" POI type',
            'validation-report.html': 'Validation report (HTML)'
        }.get(self._file_format, self._file_format)

    @property
    def compressed_title(self):
        return 'Yes' if self._is_compressed else 'No'

    @property
    def filename(self):
        return self._name

    @property
    def is_latest(self):
        return self._date == 'latest'

    @property
    def size_title(self):
        size = os.path.getsize(os.path.join(settings.LISTINGS_DIR, self._name))
        return utils.format_file_size(size)
    

def filter_none_values(lst):
    return [i for i in lst if i is not None]


def index(request):
    all_listings = filter_none_values(
        WikivoyageListingsFile.parse(filename) 
        for filename in os.listdir(settings.LISTINGS_DIR)
    )
    latest_listings = [l for l in all_listings if l.is_latest]
    latest_listings = sorted(latest_listings, key=lambda l: (l.language_code, l.file_format))
    context = {
        'latest_listings': latest_listings,
        'languages': languages.Languages.get_all_languages()
    }
    return render(request, 'wvpoi/index.html', context)


def listings(request):
    all_listings = filter_none_values(
        WikivoyageListingsFile.parse(filename) 
        for filename in os.listdir(settings.LISTINGS_DIR)
    )
    all_listings = sorted(all_listings, key=lambda l: (l.date_title, l.language_code, l.file_format))
    context = {
        'all_listings': all_listings,
        'languages': languages.Languages.get_all_languages()
    }
    return render(request, 'wvpoi/listings.html', context)


def tool(request):
    context = {
        'languages': languages.Languages.get_all_languages()
    }
    return render(request, 'wvpoi/tool.html', context)

def map_view(request):
    return render(request, 'wvpoi/map.html')

def get_listings(request):
    result = []

    filter_language = request.GET.get('language', '')
    filter_dict = {}
    excludes = None

    query = Q()

    if filter_language:
        query &= Q(language=filter_language)

    filter_article = request.GET.get('article', '')
    if filter_article:
        query &= Q(article=filter_article)

    positional_data = request.GET.get('positional_data', '')
    if positional_data == 'true':
        query &= Q(latitude__isnull=False) & Q(longitude__isnull=False)

    max_latitude = request.GET.get('max_latitude', '')
    if max_latitude != '':
        query &= Q(latitude__lte=max_latitude)

    min_latitude = request.GET.get('min_latitude', '')
    if min_latitude != '':
        query &= Q(latitude__gte=min_latitude)

    max_longitude = request.GET.get('max_longitude', '')
    if max_longitude != '':
        query &= Q(longitude__lte=max_longitude)

    min_longitude = request.GET.get('min_longitude', '')
    if min_longitude != '':
        query &= Q(longitude__gte=min_longitude)

    output_format = request.GET.get('format', 'json')
    if output_format == 'geojson':
        writer = GEOJSONOutpuFormat()
    else:
        writer = PlainJSONOutputFormat()

    listings_iter = models.Listing.objects.filter(query)

    limit = request.GET.get('limit', None)
    if limit is not None:
        listings_iter = listings_iter[:limit]
    listings_iter = listings_iter.iterator()

    response = StreamingHttpResponse(writer.iter_data(listings_iter))
    return response

def api(request):
    return render(request, 'wvpoi/api.html')

class OutputFormat(object):
    def iter_data(self, listings):
        raise NotImplementedError()

class PlainJSONOutputFormat(OutputFormat):
    def iter_data(self, listings):
        yield '[\n'
        has_previous = False
        for listing in listings:
            if has_previous:
                yield ',\n'
            yield json.dumps({
                'title': listing.title,
                'language': listing.language,
                'article': listing.article,
                'type': listing.type,
                'latitude': str(listing.latitude),
                'longitude': str(listing.longitude)
            }) 
            has_previous = True
        yield '\n]'

class GEOJSONOutpuFormat(OutputFormat):
    def iter_data(self, listings):
        yield '{"type": "FeatureCollection", "features": [\n'
        has_previous = False
        for listing in listings:
            if has_previous:
                yield ',\n'
            yield json.dumps({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(listing.longitude), float(listing.latitude)]
                },
                "properties": {
                    "name": listing.title,
                    "description": listing.description,
                    "type": listing.type,
                    "wvpoiId": listing.id,
                    "article": listing.article
                }
            }) 
            has_previous = True
        yield '\n]}'
