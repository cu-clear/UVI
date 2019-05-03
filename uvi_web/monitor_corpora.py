import pyinotify
import build_mongo_collections
import datetime
import sys

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event):
        if event.wd == 1:
            print("Modification detected in VerbNet Corpus: "+datetime.datetime.now().isoformat())
            build_mongo_collections.build_verbnet_collection()
            print("Rebuild complete: "+datetime.datetime.now().isoformat())

        elif event.wd == 2:
            print("Modification detected in VerbNet References Corpus: "+datetime.datetime.now().isoformat())
            build_mongo_collections.build_verbnet_collection()
            print("Rebuild complete: "+datetime.datetime.now().isoformat())

        elif event.wd == 3:
            print("Modification detected in PropBank Corpus at "+datetime.datetime.now().isoformat())
            build_mongo_collections.build_propbank_collection()
            print("Rebuild complete: "+datetime.datetime.now().isoformat())

        elif event.wd == 4:
            print("Modification detected in FrameNet Corpus at "+datetime.datetime.now().isoformat())
            build_mongo_collections.build_framenet_collection()
            print("Rebuild complete: "+datetime.datetime.now().isoformat())

    def process_IN_DELETE(self, event):
        if event.wd == 1:
            print("Deletion detected in VerbNet Corpus: "+datetime.datetime.now().isoformat())
            build_mongo_collections.build_verbnet_collection()
            print("Rebuild complete: "+datetime.datetime.now().isoformat())

        elif event.wd == 2:
            print("Deletion detected in VerbNet References Corpus: "+datetime.datetime.now().isoformat())
            build_mongo_collections.build_verbnet_collection()
            print("Rebuild complete: "+datetime.datetime.now().isoformat())

        elif event.wd == 3:
            print("Deletion detected in PropBank Corpus: "+datetime.datetime.now().isoformat())
            build_mongo_collections.build_propbank_collection()
            print("Rebuild complete: "+datetime.datetime.now().isoformat())

        elif event.wd == 4:
            print("Deletion detected in FrameNet Corpus: "+datetime.datetime.now().isoformat())
            build_mongo_collections.build_framenet_collection()
            print("Rebuild complete: "+datetime.datetime.now().isoformat())

    def process_IN_CREATE(self, event):
        if event.wd == 1:
            print("New file detected in VerbNet Corpus: "+datetime.datetime.now().isoformat())
            build_mongo_collections.build_verbnet_collection()
            print("Rebuild complete: "+datetime.datetime.now().isoformat())
        elif event.wd == 2:
            print("New file detected in VerbNet Referenes Corpus "+datetime.datetime.now().isoformat())
            build_mongo_collections.build_verbnet_collection()
            print("Rebuild complete "+datetime.datetime.now().isoformat())
        elif event.wd == 3:
            print("Deletion detected in PropBank Corpus "+datetime.datetime.now().isoformat())
            build_mongo_collections.build_propbank_collection()
            print("Rebuild complete "+datetime.datetime.now().isoformat())
        elif event.wd == 4:
            print("Deletion detected in FrameNet Corpus "+datetime.datetime.now().isoformat())
            build_mongo_collections.build_framenet_collection()
            print("Rebuild complete: "+datetime.datetime.now().isoformat())


def notifier_loop(notifier):
    print('Monitoring corpora for changes: '+datetime.datetime.now().isoformat())
    try:
        notifier.loop()
    except Exception as err:
        print('Exception encountered while rebuilding MongoDB collections from corpora: '+datetime.datetime.now().isoformat())
        print('Error Message is as follows:\n'+str(err))
        print('\n\nContinuing monitoring operations...')
        notifier_loop(notifier)

#Rebuild all collections once on start
print("Building all collections and monitoring corpora: "+datetime.datetime.now().isoformat())
build_mongo_collections.build_verbnet_collection()
build_mongo_collections.build_propbank_collection()
build_mongo_collections.build_framenet_collection()
build_mongo_collections.add_onto_to_db()


watch_manager = pyinotify.WatchManager()

wdd_vn = watch_manager.add_watch('../corpora/verbnet', pyinotify.ALL_EVENTS)
wdd_vn_refs = watch_manager.add_watch('../corpora/reference_docs', pyinotify.ALL_EVENTS)
wdd_pb = watch_manager.add_watch('../corpora/propbank/frames', pyinotify.ALL_EVENTS)
wdd_fn = watch_manager.add_watch('../corpora/framenet', pyinotify.ALL_EVENTS)
wdd_on = watch_manager.add_watch('../corpora/ontonotes', pyinotify.ALL_EVENTS)

handler = EventHandler()
notifier = pyinotify.Notifier(watch_manager, handler)

notifier_loop(notifier)
