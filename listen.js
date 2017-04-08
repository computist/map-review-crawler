(function() {
    var proxied = window.XMLHttpRequest.prototype.open;
    window.XMLHttpRequest.prototype.open = function(method, url) {
        if (url.startsWith("/search")) {
            var pointer = this
            var intervalId = window.setInterval(function(){
                    if(pointer.readyState != 4){
                        return;
                    }
                    var resArray = pointer.responseText.split("ludocid\\\\u003d"); 
                    var cids = [];
                    for (var i = 1 /*skip first junk*/; i < resArray.length; i += 2 /*duplicate*/) {
                        cids[(i-1)/2] = resArray[i].substring(0, resArray[i].indexOf("#lrd"));
                    }
                    var tag = document.createElement("script");
                    tag.src = 'https://localhost:5000?cids=' + cids;
                    document.getElementsByTagName("head")[0].appendChild(tag);
                    clearInterval(intervalId);
            }, 1);
        }
        return proxied.apply(this, [].slice.call(arguments));
    };
})();