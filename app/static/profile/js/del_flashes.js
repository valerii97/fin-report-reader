setTimeout(function(){
    var box = document.getElementById("fl");
    var oppArray = ["0.9", "0.8", "0.7", "0.6", "0.5", "0.4", "0.3", "0.2", "0.1", "0"];
    var x = 0;
    (function next() {
        box.style.opacity = oppArray[x];
        if(++x < oppArray.length) {
            setTimeout(next, 100); //depending on how fast you want to fade
        }
    })();
}, 2000);

setTimeout(function(){
    document.getElementById("fl").style.display = "None";
}, 3100);