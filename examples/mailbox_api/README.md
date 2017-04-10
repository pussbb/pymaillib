```bash
$ wget -O- http://0.0.0.0:5050/api/mailbox/

```

```json
"folders": {
    "021222891bee54b4abfec51e8b845235": {
        "class": null,
        "delimiter": "/",
        "dref": "021222891bee54b4abfec51e8b845235",
        "editable": true,
        "modified": null,
        "name": "Public Folders/Test",
        "special_folder": false,
        "stats": {},
        "total": 0,
        "unread": 0
    },
}
```

```bash
$ wget -O- http://0.0.0.0:5050/api/mailbox/d54aa894f6e0503d9f865062aec2e98c
```

```json
[
  {
    "BODYSTRUCTURE": [ {
        "attributes": {},
        "boundary": "----=_Part_3_952119285.1487835648083",
        "content_part": "multipart/alternative",
        "disposition": null,
        "language": null,
        "location": null,
        "main_type": "multipart",
        "mime_id": "0",
        "subtype": "alternative"
      }, {
        "attributes": {},
        "charset": "us-ascii",
        "content_part": "text/plain",
        "description": null,
        "disposition": {},
        "encoding": "7bit",
        "filename": null,
        "language": null,
        "location": null,
        "main_type": "text",
        "md5": null,
        "mime_id": "1",
        "name": "",
        "part_id": "0001620569cb7534.1@test.centosx64.com",
        "size": 118,
        "subtype": "plain",
        "text_size": 4
    }, {
    "attributes": {},
    "charset": null,
    "content_part": "application/rtf",
    "description": null,
    "disposition": {},
    "encoding": "7bit",
    "filename": null,
    "language": null,
    "location": null,
    "main_type": "application",
    "md5": null,
    "mime_id": "2",
    "name": "",
    "part_id": "0001620569cb7534.2@test.centosx64.com",
    "size": 153,
    "subtype": "rtf",
    "text_size": null
    }, {
        "attributes": {
          "method": "REQUEST"
        },
        "charset": "UTF-8",
        "content_part": "text/calendar",
        "description": null,
        "disposition": {},
        "encoding": "8bit",
        "filename": null,
        "language": null,
        "location": null,
        "main_type": "text",
        "md5": null,
        "mime_id": "3",
        "name": "meeting.ics",
        "part_id": null,
        "size": 1353,
        "subtype": "calendar",
        "text_size": 47
    }],
    "ENVELOPE": {
        "bcc": [],
        "cc": [],
        "date": "Thu, 23 Feb 2017 02:40:48 GMT",
        "from_": [
          {
            "addr_spec": "sxadmin-test@allwebsuite.com",
            "display": "sxadmin<sxadmin-test@allwebsuite.com>",
            "host": "allwebsuite.com",
            "mailbox": "sxadmin-test",
            "name": "sxadmin",
            "route": null
          }
        ],
        "in_reply_to": null,
        "message_id": "<1712302357.61487835648086.JavaMail.root@test.centosx64.com>",
        "reply_to": [
          {
            "addr_spec": "sxadmin-test@allwebsuite.com",
            "display": "sxadmin<sxadmin-test@allwebsuite.com>",
            "host": "allwebsuite.com",
            "mailbox": "sxadmin-test",
            "name": "sxadmin",
            "route": null
          }
        ],
        "sender": [
           {
            "addr_spec": "sxadmin-test@allwebsuite.com",
            "display": "sxadmin<sxadmin-test@allwebsuite.com>",
            "host": "allwebsuite.com",
            "mailbox": "sxadmin-test",
            "name": "sxadmin",
            "route": null
            }
        ],
        "subject": "qwdqwd dsfdsf sfdsfdsf",
        "to": [
          {
            "addr_spec": "test.test@allwebsuite.com",
            "display": "test test<test.test@allwebsuite.com>",
            "host": "allwebsuite.com",
            "mailbox": "test.test",
            "name": "test test",
            "route": null
          }
        ],
    },
    "FLAGS": ["\Seen", "X-Scalix-Processed"],
    "RFC822.SIZE": 2791,
    "SEQ": 1,
    "UID": 6,
    "folder": {
        "class": null,
        "delimiter": "/",
        "dref": "d54aa894f6e0503d9f865062aec2e98c",
        "editable": false,
        "modified": null,
        "name": "INBOX",
        "special_folder": true,
        "stats": {},
        "total": 0,
        "unread": 0
        }
}]
```


```bash
$ wget -O- http://0.0.0.0:5050/api/mailbox/d54aa894f6e0503d9f865062aec2e98c/61/  
#you will get RFC822 email

$ wget -O- http://0.0.0.0:5050/api/mailbox/d54aa894f6e0503d9f865062aec2e98c/61/{part_id}
#- decoded part id, if set ?raw=DOESNOTMETTER you will get raw msg part
```
