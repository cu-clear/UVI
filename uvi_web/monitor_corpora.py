import pyinotify
import build_mongo_collections
import datetime

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event):
        if event.wd == 1:
            print("Modification detected in VerbNet Corpus. Rebuilding MongoDB Collection(s) ['verbnet']...")
            build_mongo_collections.build_verbnet_collection()
            print("Rebuild complete.")

        elif event.wd == 2:
            print("Modification detected in VerbNet References Corpus. Rebuilding MongoDB Collection(s) ['verbnet']...")
            build_mongo_collections.build_verbnet_collection()
            print("Rebuild complete.")

        elif event.wd == 3:
            print("Modification detected in PropBank Corpus. Rebuilding MongoDB Collection(s) ['propbank']...")
            build_mongo_collections.build_propbank_collection()
            print("Rebuild complete.")

        elif event.wd == 4:
            print("Modification detected in FrameNet Corpus. Rebuilding MongoDB Collection(s) ['framenet']...")
            build_mongo_collections.build_framenet_collection()
            print("Rebuild complete.")

    def process_IN_DELETE(self, event):
        if event.wd == 1:
            print("Deletion detected in VerbNet Corpus. Rebuilding MongoDB Collection(s) ['verbnet']...")
            build_mongo_collections.build_verbnet_collection()
            print("Rebuild complete.")

        elif event.wd == 2:
            print("Deletion detected in VerbNet References Corpus. Rebuilding MongoDB Collection(s) ['verbnet']...")
            build_mongo_collections.build_verbnet_collection()
            print("Rebuild complete.")

        elif event.wd == 3:
            print("Deletion detected in PropBank Corpus. Rebuilding MongoDB Collection(s) ['propbank']...")
            build_mongo_collections.build_propbank_collection()
            print("Rebuild complete.")

        elif event.wd == 4:
            print("Deletion detected in FrameNet Corpus. Rebuilding MongoDB Collection(s) ['framenet']...")
            build_mongo_collections.build_framenet_collection()
            print("Rebuild complete.")

    def process_IN_CREATE(self, event):
        if event.wd == 1:
            print("New file detected in VerbNet Corpus. Rebuilding MongoDB Collection(s) ['verbnet']...")
            build_mongo_collections.build_verbnet_collection()
            print("Rebuild complete.")
        elif event.wd == 2:
            print("New file detected in VerbNet Referenes Corpus. Rebuilding MongoDB Collection(s) ['verbnet']...")
            build_mongo_collections.build_verbnet_collection()
            print("Rebuild complete.")
        elif event.wd == 3:
            print("Deletion detected in PropBank Corpus. Rebuilding MongoDB Collection(s) ['propbank']...")
            build_mongo_collections.build_propbank_collection()
            print("Rebuild complete.")
        elif event.wd == 4:
            print("Deletion detected in FrameNet Corpus. Rebuilding MongoDB Collection(s) ['framenet']...")
            build_mongo_collections.build_framenet_collection()
            print("Rebuild complete.")


def notifier_loop(notifier):
    print('Monitoring corpora for changes...')
    try:
        notifier.loop()
    except Exception as err:
        print('Uh oh, error while rebuilding MongoDB collections from corpora:')
        print(err)
        print('Continuing monitoring operations...')
        notifier_loop(notifier)

#Rebuild all collections once on start
build_mongo_collections.build_verbnet_collection()
build_mongo_collections.build_propbank_collection()
build_mongo_collections.build_framenet_collection()


watch_manager = pyinotify.WatchManager()

wdd_vn = watch_manager.add_watch('../corpora/verbnet', pyinotify.ALL_EVENTS)
wdd_vn_refs = watch_manager.add_watch('../reference_docs', pyinotify.ALL_EVENTS)
wdd_pb = watch_manager.add_watch('../corpora/propbank/frames', pyinotify.ALL_EVENTS)
wdd_fn = watch_manager.add_watch('../corpora/framenet', pyinotify.ALL_EVENTS)
#wdd_on = watch_manager.add_watch('../corpora/ontonotes', pyinotify.ALL_EVENTS)

handler = EventHandler()
notifier = pyinotify.Notifier(watch_manager, handler)

notifier_loop(notifier)



# cur_time_str = datetime.datetime.now().isoformat()
# with open('logs/corpus_change_detection_'+cur_time_str, 'w') as logfile: