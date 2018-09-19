import os
import json
from collections import OrderedDict
from copy import deepcopy
import settings


def main():
    index = load_resource(settings.INDEX_MEDIA + "index_media.json")
    speech = index["ID191002001"]
    make_manifest(speech)
    make_annotations(speech)


def make_manifest(speech):
    manifest = deepcopy(settings.MANIFEST)
    identifier = speech["id"]
    manifest["id"] = get_uri(identifier, settings.MANIFEST_ID_TEMPLATE)
    manifest["label"] = lang_de(speech["headline"])
    add_metadata(manifest, "wahlperiode", speech)
    add_metadata(manifest, "sitzungsnummer", speech)
    add_metadata(manifest, "date", speech)
    add_metadata(manifest, "rednerID", speech)   
    canvas = manifest["items"][0]
    canvas["id"] = get_uri(identifier, settings.CANVAS_URI_TEMPLATE)
    canvas["duration"] = speech["duration"]
    annopage = canvas["items"][0]
    annopage["id"] = get_uri(identifier, settings.ANNOPAGE_URI_TEMPLATE)
    content_anno = annopage["items"][0]
    content_anno["id"] = get_uri(identifier, settings.ANNO_URI_TEMPLATE)
    content_anno["body"]["id"] = settings.VIDEO_URI_TEMPLATE.format(speech["mediaID"])
    content_anno["body"]["duration"] = speech["duration"]
    content_anno["target"] = canvas["id"]
    canvas["annotations"][0]["id"] = get_uri(identifier, settings.TRANSCRIPT_ID_TEMPLATE)

    manifest_path = os.path.join("../iiif", identifier + ".json")
    save_resource(manifest, manifest_path)


def get_uri(identifier, template):
    part = template.format(identifier)
    return settings.DOMAIN + part


def add_metadata(manifest, key, speech):
    manifest["metadata"].append({
        "label": lang_de(key),
        "value": lang_de(speech[key])
    })


def make_annotations(speech):
    path = "{0}{1}/{2}/{1}{2}-Rede-{3}.vtt".format(
        settings.INDEX_MEDIA,
        speech["wahlperiode"],
        speech["sitzungsnummer"].zfill(3),
        speech["id"])
    print(path)
    vtt_lines = load_lines(path)
    for line in vtt_lines:
        print(line)

    # vtt = WebVTTFile.open("pets-en.vtt")
    # canvas = "http://example.org/canvas/1"
    # annos = []
    # for caption in vtt:
    #     tgt = "%s#t=npt:%s,%s" % (canvas, caption.start, caption.end)
    #     annos.append({"@type": "Annotation", "motivation": "painting", "body": {"value": caption.text}, "target": tgt})
    # al = {"@type": "AnnotationList", "items": annos}
    # print json.dumps(al, sort_keys=True, indent=4)


def lang_de(text):
    return { "de": [ text ] }


def load_resource(file_path):
    with open(file_path) as json_data:
        return json.load(json_data, object_pairs_hook=OrderedDict)


def load_lines(file_path):
    with open(file_path) as line_source:
        src = line_source.readlines()
        return [x.strip() for x in src] 

def save_resource(resource, file_path):
    with open(file_path, 'w') as outfile:
        json.dump(resource, outfile, indent=4)


if __name__ == "__main__":
    main()