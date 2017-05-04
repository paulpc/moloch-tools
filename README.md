A few tools developped through the firehose incident of accidental upgrade of ES.
***THIS IS DANGEROUS STUFF, I WROTE IT OUT OF DESPERATION TO FIX A REALLY BROKEN CLUSTER. USE AT YOUR OWN RISK***

The problem started by not looking at the warnining for upgrading indices before upgrading ElasticSearch to 5.3 from 2.4.1. Upgrading in a flash test environment worked great, as it didn't have any indices created in the pre 2.x ElasticSearch world. 

Once everything was messsed up, I realized i needed a good way to shut down / start up the environment. Cue the bash scripts. Rename the capture.txt, viewer.txt, eshosts.txt to remove the \_template suffix. Then you can go into the files and set up your environment. The scripts assume the machines running the environment have the same user that's logged in into the one starting all these jobs. However, you can probably hack it to work by adding username@hostname per line in the txt files in stead of just hostname per line.

The oddest thing I noticed from the failed upgrade was that ES renamed a bunch of the indices to their UUID, whilst keeping an empty copy of the actual name. I got some limited success in renaming the folders, but I realized this was super risky. Next best thing was to reindex the documents in the right indices. Cue the python script. It will use multiprocessing, the Scroll API, and the Bulk API to move documents from one index to another. It detects the messed up indices by looking for indices where uuid == index name. Then it saves a map of the {uuid:index\_name} and saves it to disk (I was too lazy to do proper multiprocessing and used the Pool API).

