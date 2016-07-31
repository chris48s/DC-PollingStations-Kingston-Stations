import geojson
import json
import os
import urllib.request

# hack to override sqlite database filename
# see: https://help.morph.io/t/using-python-3-with-morph-scraperwiki-fork/148
os.environ['SCRAPERWIKI_DATABASE_NAME'] = 'sqlite:///data.sqlite'
import scraperwiki


url = "http://www6.kingston.gov.uk/ArcGISServer/rest/services/polling/polling_Districts_Stations/MapServer/0/query?geometry=&geometryType=esriGeometryPoint&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&objectIds=&where=OBJECTID+LIKE+%27%25%27&time=&returnCountOnly=false&returnIdsOnly=false&returnGeometry=true&maxAllowableOffset=&outSR=&outFields=*&f=pjson"
uk_grid = geojson.crs.Named(
    properties={ "name": "urn:ogc:def:crs:EPSG::27700" }
)
council_id = 'E09000021'


def format_address(in_addr):
    address_parts = in_addr.split(', ')
    address_parts = [x.strip() for x in address_parts]
    postcode = address_parts[-1]
    postcode = postcode.replace(u'\xa0', u' ')
    address = "\n".join(address_parts[:-1])

    return (address, postcode)


with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode('utf-8'))
    for feature in data['features']:
        location = geojson.Point((feature['geometry']['x'], feature['geometry']['y']), crs=uk_grid)

        address, postcode = format_address(feature['attributes']['LOCATION'])

        record = {
            'internal_council_id': feature['attributes']['ATT2'],
            'polling_district_id': feature['attributes']['ATT2'],
            'address': address,
            'postcode': postcode,
            'location': geojson.dumps(location),
            'council_id': council_id
        }

        scraperwiki.sqlite.save(unique_keys=['internal_council_id'], data=record, table_name='data')
