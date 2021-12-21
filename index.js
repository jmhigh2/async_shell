
let url = "ws://localhost:60000/ws"

let initialized = false;

while (!initialized) {
    try 
    {
        var ws = new WebSocket(url);
        ws.onmessage = function(evt) {
            console.log(evt.data)

        } 
        initialized = true;
        console.log(ws)

    }

    catch
    {
        console.log("here")
    }
}




