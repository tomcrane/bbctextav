import os
import datetime
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
    identifier = speech["id"]
    path = "{0}{1}/{2}/{1}{2}-Rede-{3}.vtt".format(
        settings.INDEX_MEDIA,
        speech["wahlperiode"],
        speech["sitzungsnummer"].zfill(3),
        identifier)
    print(path)
    vtt_lines = load_lines(path)
    captions = []
    caption = None
    counter = 1
    while counter < len(vtt_lines):
        line = vtt_lines[counter]
        if line == "":
            if caption is not None:
                captions.append(caption)
            if counter < len(vtt_lines) - 4:
                caption = {
                    "id": get_uri("text-" + vtt_lines[counter + 1], settings.CAPTION_URI_TEMPLATE),
                    "fragment": get_t_fragment(vtt_lines[counter + 2]),
                    "text": vtt_lines[counter + 3]
                }
            counter = counter + 4

    transcript = deepcopy(settings.TRANSCRIPT_PAGE)
    transcript["id"] = get_uri(identifier, settings.TRANSCRIPT_ID_TEMPLATE)
    for caption in captions:
        transcript["items"].append(make_anno(caption, speech))

    transcript_path = os.path.join("../iiif", identifier + "-transcript.json")
    save_resource(transcript, transcript_path)


def make_anno(caption, speech):
    anno = deepcopy(settings.TRANSCRIPT_ANNO)
    anno["id"] = caption["id"]
    anno["body"]["value"] = caption["text"]
    target_uri = get_uri(speech["id"], settings.CANVAS_URI_TEMPLATE)
    anno["target"] = target_uri + caption["fragment"]
    return anno


def get_t_fragment(webvtt_t):
    parts = webvtt_t.split()
    return "#t={0},{1}".format(as_seconds(parts[0]), as_seconds(parts[2]))


def as_seconds(smpte):
    # 00:05:05.020
    d = smpte.split(":")
    seconds = float(d[0]) * 3600 + float(d[1]) * 60 + float(d[2])
    return str(seconds)


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
        json.dump(resource, outfile, sort_keys=True, indent=4)


if __name__ == "__main__":
    main()