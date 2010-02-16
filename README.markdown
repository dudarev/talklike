To start running on localhost

    git pull git://github.com/dudarev/talklike.git
    cd talklike
    dev_appserver code

Browse to http://localhost:8080/admin
New > Language 
Fill in:

    Language code: en
    Dictionary link: http://onelook.com/?w=
    Translate to by default: ru

New > Section
Fill in

    Section name: obama
    Feed URL: feedburner_URL
    Language: en

Upload a backup file 
data_backup/20090311/obama.xml
Browse to Section: Edit obama
On this page click "Make first".
Go to http://localhost:8080/obama
