import xml.etree.ElementTree as ET
import sys

DRM_TO_OSM_HIGHWAY = {
    '1': 'motorway',     # 高速自動車国道
    '2': 'motorway',     # 都市高速道路
    '3': 'trunk',        # 一般国道
    '4': 'primary',      # 主要地方道（都道府県道）
    '5': 'secondary',    # 主要地方道（指定市道）
    '6': 'secondary',    # 一般都道府県道
    '7': 'tertiary',     # 指定市の一般市道
    '9': 'unclassified', # その他道路
}

def main(input_file, output_file):
    # Parse file OSM
    tree = ET.parse(input_file)
    root = tree.getroot()

    for way in root.findall('way'):
        spec_tag = next((t for t in way.findall('tag') if t.get('k') == '_種別CD_'), None)
        osm_value = None

        if spec_tag is not None:
            code = spec_tag.get('v')
            osm_value = DRM_TO_OSM_HIGHWAY.get(code)
        
        if osm_value is None:
            osm_value = 'residential'

        hw_tag = next((t for t in way.findall('tag') if t.get('k') == 'highway'), None)
        if hw_tag is not None:
            hw_tag.set('v', osm_value)
        else:
            ET.SubElement(way, 'tag', k='highway', v=osm_value)

    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"Wrote output to {output_file}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python fill_osm_tags.py input.osm output.osm')
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
