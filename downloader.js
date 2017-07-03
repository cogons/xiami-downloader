var fs = require("fs");
var _ = require('underscore')
var path = require('path');
var request = require('request');
var Bagpipe = require('bagpipe');
var bagpipe = new Bagpipe(3);

function readfile(path) {
    return JSON.parse(JSON.stringify(fs.readFileSync(path).toString().split("\n"))).filter((doc => {
        if (doc.length > 1) return 1
        else return 0
    })).map((doc) => {
        return ((JSON.parse(doc).result))
    }).filter((doc) => {
        return doc.ourl.length > 0 && doc.title.indexOf("ive") == -1
    })
}

var docs = _.map(readfile("./hebe.json"), extract)

function extract(doc) {

    return {
        title: doc.title.replace("/", ""),
        url: doc.ourl
    }

}

var index = 1;

var downloader = function(src, dest, callback) {
    request.head(src, function(err, res, body) {
        // console.log('content-type:', res.headers['content-type']);
        // console.log('content-length:', res.headers['content-length']);
        if (src) {
            request(src).pipe(fs.createWriteStream(dest)).on('close', function() {
                callback(null, dest);
            });
        }

    });

};


var files = docs
for (var i = 0; i < files.length; i++) {
    var dest = "./songs/" + files[i].title + ".mp3";
    if (!fs.exists(dest)) {
        bagpipe.push(downloader, files[i], dest, function(err, data) {
            console.log("[" + index++ + "]: " + data);
        });
    }
}
console.log("complete", i)